# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-29 22:04


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0018_customreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customreport',
            name='title',
            field=models.CharField(max_length=80),
        ),
    ]
