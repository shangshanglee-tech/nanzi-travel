from django import forms

from .models import Product, Vessel


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


class VesselAdminForm(forms.ModelForm):
    class Meta:
        model = Vessel
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get("features")
        if value is None:
            return cleaned_data
        if not isinstance(value, list):
            self.add_error("features", "内容必须是列表，例如：[\"科学中心\", \"全景酒廊\"]")
        elif any(not isinstance(item, str) or not item.strip() for item in value):
            self.add_error("features", "列表中不能包含非文字内容或空白项")
        return cleaned_data
