# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-22 21:30


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0008_auto_20160311_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='notes',
            field=models.TextField(default=b'No sensor notes available.', verbose_name=b'Please enter descriptive notes about the sensor.'),
        ),
    ]
