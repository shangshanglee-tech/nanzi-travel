from django.db import migrations


def register_existing_images(apps, schema_editor):
    MediaAsset = apps.get_model("catalog", "MediaAsset")
    sources = (
        (apps.get_model("catalog", "Vessel"), "card_image", "船只卡片图"),
        (apps.get_model("catalog", "VesselPageBlock"), "image", "船只内容图"),
        (apps.get_model("catalog", "VesselPageBlockImage"), "image", "船只内容附图"),
        (apps.get_model("catalog", "CabinType"), "image", "舱位图"),
        (apps.get_model("catalog", "VesselDeckPlan"), "image", "甲板图"),
        (apps.get_model("catalog", "Product"), "hero_image", "路线主图"),
        (apps.get_model("catalog", "ProductImage"), "image", "路线图库"),
        (apps.get_model("catalog", "Activity"), "hero_image", "活动主图"),
        (apps.get_model("catalog", "ActivityImage"), "image", "活动图库"),
    )
    for model, field_name, title in sources:
        for item in model.objects.exclude(**{field_name: ""}):
            image_name = getattr(item, field_name).name
            if image_name:
                MediaAsset.objects.get_or_create(image=image_name, defaults={"title": title})


class Migration(migrations.Migration):
    dependencies = [("catalog", "0019_media_asset_library")]

    operations = [migrations.RunPython(register_existing_images, migrations.RunPython.noop)]
