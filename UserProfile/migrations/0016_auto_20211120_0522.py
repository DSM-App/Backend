# Generated by Django 3.2.3 on 2021-11-20 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0015_auto_20211025_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='private_key',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='public_key',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]