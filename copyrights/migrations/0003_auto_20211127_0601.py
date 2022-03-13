# Generated by Django 3.2.3 on 2021-11-27 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copyrights', '0002_auto_20211127_0322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='copyright',
        ),
        migrations.AlterField(
            model_name='ownershipcopyrights',
            name='copyrighted_votes',
            field=models.ManyToManyField(related_name='copyrights_voted', to='copyrights.Vote'),
        ),
        migrations.AlterField(
            model_name='ownershipcopyrights',
            name='not_copyrighted_votes',
            field=models.ManyToManyField(related_name='not_copyrights_voted', to='copyrights.Vote'),
        ),
    ]