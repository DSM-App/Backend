# Generated by Django 3.2.3 on 2021-11-21 07:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20211121_0742'),
        ('posts', '0014_alter_blogpost_digital_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='group_blogposts', to='groups.group'),
        ),
    ]
