import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_add_stock_movement"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimage",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name="productimage",
            index=models.Index(
                fields=["instrument", "is_main"],
                name="prodimg_inst_ismain_idx",
            ),
        ),
    ]
