from django import forms

from .models import Product


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
