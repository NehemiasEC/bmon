# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-06-30 01:12


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bmsapp', '0021_auto_20170502_1231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertrecipient',
            name='cell_sms_gateway',
            field=models.CharField(blank=True, choices=[(b'msg.acsalaska.com', b'Alaska Communications (ACS)'), (b'txt.att.net', b'AT&T'), (b'cingular.com', b'Cingular'), (b'mobile.gci.net', b'General Communications Inc. (GCI)'), (b'sms.mtawireless.com', b'MTA Wireless'), (b'messaging.sprintpcs.com', b'Sprint'), (b'tmomail.net', b'T-Moble'), (b'vtext.com', b'Verizon Wireless')], max_length=60, verbose_name=b'Cell Phone Carrier'),
        ),
        migrations.AlterField(
            model_name='building',
            name='report_footer',
            field=models.TextField(blank=True, default=b'', help_text=b'Use <a href="http://markdowntutorial.com/"> markdown syntax </a> to add links, pictures, etc.  Note that you <b>must</b> include the url prefix (e.g. <i>http://</i>) in your links.', verbose_name=b'Additional Building Documentation'),
        ),
    ]
