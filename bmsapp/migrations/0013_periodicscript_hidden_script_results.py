# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-02 18:16


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0012_periodicscript_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodicscript',
            name='hidden_script_results',
            field=models.TextField(blank=True, verbose_name=b'Hidden Script results in YAML form'),
        ),
    ]
