import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_shipping_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="payment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="historicalpayment",
            name="updated_at",
            field=models.DateTimeField(blank=True, editable=False, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
