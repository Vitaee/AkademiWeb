# Generated by Django 3.0.8 on 2020-07-05 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AkademiApp', '0002_auto_20200705_1904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uyeler',
            name='Üye Puanı',
            field=models.IntegerField(),
        ),
    ]
