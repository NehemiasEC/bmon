# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-11 17:08


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0007_building_report_footer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='report_footer',
            field=models.TextField(blank=True, help_text=b'Use <a href="http://markdowntutorial.com/"> markdown syntax </a> to add links, pictures, etc.  Note that you <b>must</b> include the url prefix (e.g. <i>http://</i>) in your links.', null=True, verbose_name=b'Additional Building Documentation'),
        ),
    ]
