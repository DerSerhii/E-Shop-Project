# Generated by Django 4.0.5 on 2022-06-26 20:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_shop', '0005_product_is_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)]),
        ),
    ]
