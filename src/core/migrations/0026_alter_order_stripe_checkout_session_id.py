# Generated by Django 3.2.18 on 2023-05-05 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_order_stripe_checkout_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stripe_checkout_session_id',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
    ]
