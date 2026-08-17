from django import forms
from django.db.models import Max

from .models import Product, VesselPageBlock, VesselPageBlockImage, VesselPageBlockType


LIST_FIELDS = (
    "tags",
    "highlights",
    "included",
    "excluded",
    "suitable_for",
    "notices",
)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        for field_name in LIST_FIELDS:
            value = cleaned_data.get(field_name)
            if value is None:
                continue
            if not isinstance(value, list):
                self.add_error(field_name, "内容必须是列表，例如：[\"摄影\", \"探险\"]")
                continue
            if any(not isinstance(item, str) or not item.strip() for item in value):
                self.add_error(field_name, "列表中不能包含非文字内容或空白项")
        return cleaned_data


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files]


class VesselPageBlockInlineForm(forms.ModelForm):
    additional_images = MultipleImageField(
        label="添加更多图片",
        required=False,
        help_text="可一次选择多张；首张图片仍使用上方“图片”字段。",
    )

    class Meta:
        model = VesselPageBlock
        fields = ("block_type", "title", "image", "body", "is_visible", "sort_order")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("additional_images") and cleaned_data.get("block_type") != VesselPageBlockType.CARD:
            self.add_error("additional_images", "只有内容卡片可以添加更多图片")
        return cleaned_data

    def save(self, commit=True):
        page_block = super().save(commit=commit)
        if not commit:
            return page_block

        images = self.cleaned_data.get("additional_images", [])
        if images:
            next_order = (page_block.additional_images.aggregate(max_order=Max("sort_order"))["max_order"] or -1) + 1
            VesselPageBlockImage.objects.bulk_create(
                [
                    VesselPageBlockImage(
                        vessel=page_block.vessel,
                        page_block=page_block,
                        image=image,
                        sort_order=next_order + index,
                    )
                    for index, image in enumerate(images)
                ]
            )
        return page_block
