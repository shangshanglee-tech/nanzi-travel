from django import forms
from django.db.models import Max
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Product, VesselDeckPlan, VesselPageBlock, VesselPageBlockImage, VesselPageBlockType


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


class AdditionalImagesPreviewWidget(forms.Widget):
    def value_from_datadict(self, data, files, name):
        if hasattr(data, "getlist"):
            return data.getlist(name)
        value = data.get(name)
        if value in (None, ""):
            return []
        return value if isinstance(value, (list, tuple)) else [value]

    def render(self, name, value, attrs=None, renderer=None):
        images = list(self.choices)
        if not images:
            return format_html('<div class="additional-images-preview additional-images-preview--empty">暂无已上传图片</div>')
        selected_ids = {str(image_id) for image_id in (value or [])}
        items = []
        image_urls = getattr(self, "image_urls", {})
        for image_id, image_name in images:
            image_url = image_urls.get(str(image_id), "")
            checked = mark_safe(" checked") if str(image_id) in selected_ids else ""
            items.append(format_html(
                '<li><a href="{}" target="_blank" rel="noopener"><img src="{}" alt="{}" style="display:block;width:180px;max-height:120px;object-fit:cover;margin:0 0 6px;border-radius:4px" /><span>{}</span></a><input type="checkbox" name="{}" value="{}"{} style="display:none" /><button type="button" data-delete-image="true" style="display:block;margin-top:6px;color:#b42318">删除图片</button></li>',
                image_url,
                image_url,
                image_name,
                image_name,
                name,
                image_id,
                checked,
            ))
        return format_html('<div class="additional-images-preview"><ul>{}</ul></div>', mark_safe("".join(items)))


class AdditionalImagesPreviewField(forms.MultipleChoiceField):
    widget = AdditionalImagesPreviewWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)


class DeckPlanImageWidget(forms.FileInput):
    """Render an existing deck plan as a preview before allowing a replacement upload."""

    def render(self, name, value, attrs=None, renderer=None):
        attrs = {**self.attrs, **(attrs or {})}
        input_id = attrs.get("id", f"id_{name}")
        file_input = format_html(
            '<input type="file" name="{}" accept=".svg,.png,.jpg,.jpeg,.webp" id="{}">',
            name,
            input_id,
        )
        if not value or not getattr(value, "url", None):
            return format_html('<div data-deck-plan-upload="true">{}</div>', file_input)

        return format_html(
            '<div data-deck-plan-upload="true">'
            '<div data-deck-plan-preview="true">'
            '<img class="deck-plan-preview-image" src="{}" alt="已上传甲板示意图">'
            '<button type="button" data-deck-plan-delete="true">删除</button>'
            '</div>'
            '<div data-deck-plan-replacement="true" hidden>{}</div>'
            '</div>',
            value.url,
            file_input,
        )


class VesselDeckPlanInlineForm(forms.ModelForm):
    class Meta:
        model = VesselDeckPlan
        fields = ("title", "image", "sort_order")
        widgets = {"image": DeckPlanImageWidget}


class VesselPageBlockInlineForm(forms.ModelForm):
    additional_images = MultipleImageField(
        label="添加更多图片",
        required=False,
        help_text="可一次选择多张；首张图片仍使用上方“图片”字段。",
    )
    existing_additional_images = AdditionalImagesPreviewField(
        label="已上传图片",
        help_text="这里展示当前已保存的附加图片，方便确认第二张及后续图片是否已经配置成功。",
    )

    class Meta:
        model = VesselPageBlock
        fields = ("block_type", "title", "image", "additional_images", "existing_additional_images", "body", "is_visible", "sort_order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_images = []
        image_urls = {}
        if self.instance and self.instance.pk:
            for image in self.instance.additional_images.order_by("sort_order", "id"):
                if image.image:
                    image_id = str(image.pk)
                    existing_images.append((image_id, image.image.name.rsplit("/", 1)[-1]))
                    image_urls[image_id] = image.image.url
        self.fields["existing_additional_images"].choices = existing_images
        self.fields["existing_additional_images"].widget.image_urls = image_urls
        self.fields["existing_additional_images"].initial = []

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
        image_ids_to_delete = self.cleaned_data.get("existing_additional_images", [])
        if image_ids_to_delete:
            page_block.additional_images.filter(pk__in=image_ids_to_delete).delete()
        return page_block
