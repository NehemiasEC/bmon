# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-31 21:38


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0015_auto_20161216_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='timeline_annotations',
            field=models.TextField(blank=True, help_text=b'One annotation per line. Use a colon between the annotation and the date/time.', verbose_name=b"Annotations for events in the building's timeline (e.g. Boiler Replaced: 1/1/2017)"),
        ),
    ]
