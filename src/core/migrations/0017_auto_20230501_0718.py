# Generated by Django 3.2.18 on 2023-05-01 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_orderitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='billing_info',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='is_cancelled',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_info',
            field=models.JSONField(blank=True, null=True),
        ),
    ]