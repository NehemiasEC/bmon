#!/usr/bin/env python3.7
"""Stores Siemens DDC point data from email messages with trend file
attachments.
"""
import readers.siemens
import mail2bmon

mail2bmon.process_email(r'.+\.csv$', readers.siemens.parse_file, 'US/Alaska')
