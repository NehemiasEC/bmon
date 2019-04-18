﻿'''
Module used to store incoming sensor readings in the database.
'''

import dateutil.parser
import calendar
import re
import time
import logging

from . import models
from .readingdb import bmsdata
from .calcs import transforms

# Make a logger for this module
_logger = logging.getLogger('bms.' + __name__)

def convert_val(ts, reading_id, val, db):
    """Takes a raw reading values 'ts', 'reading_id', and 'val' and converts them
    to a form suitable for storage in the reading database.  If a transform 
    function applies to the reading_id, it is applied.  Also, non-numerical 
    string 'val's are converted to numeric values suitable for storage as a float.
    'db' is a bmsdata.BMSdata reading database object.
    Returned is the tuple (ts, reading_id, val) as any of these could be
    transformed by the transform function.
    """

    # get the Sensor object, if available, to see if there is a transform function
    sensors = models.Sensor.objects.filter( sensor_id=reading_id )
    if len(sensors)>0:
        # Take first sensor in list ( should be only one ) and get transform function & parameters
        transform_func = sensors[0].tran_calc_function
        transform_params = sensors[0].function_parameters
    else:
        # no sensor with the requested ID was found.  Therefore, no transform function and parameters.
        transform_func = ''
        transform_params = ''

    # If val is a string, decode it into a float value
    if type(val) in (str, str):
        if ('True' in val) or ('Closed' in val) or ('On' in val) or (val.startswith('Motion') or (val.startswith('Light')) or (val.startswith('Voltage'))):
            val = 1.0
        elif  ('False' in val) or ('Open' in val) or ('Off' in val) or (val.startswith('No')):
            val = 0.0
        else:
            # convert to float the first decimal number
            parts = re.match(r'(-?\d+)\.?(\d+)?', val).groups('0')
            val = float( parts[0] + '.' + parts[1] )

    # if there is a transform function passed, use it to convert the reading values
    if len(transform_func.strip()):
        trans = transforms.Transformer(db)
        ts, reading_id, val = trans.transform_value(ts, reading_id, val, transform_func, transform_params)

    return ts, reading_id, val

def store(reading_id, request_data):
    """Stores a reading into the Reading database.
    'reading_id' is the ID of the sensor or calculated reading to store.
    'request_data' is a dictionary containing the rest of the information related to the reading:
        The 'val' key holds the value to store.  See code in convert_val() method
            for various formats that 'val' can take.
        The optional 'ts' key holds a date/time string in UTC for the timestamp 
            of the reading. If not present, the current time is used.
    Returns the message returned by the database insert method.
    """

    # open the database 
    db = bmsdata.BMSdata()
    
    # parse the date into a datetime object and then into Unix seconds. Convert to
    # integer.
    if 'ts' in request_data:
        ts = int( calendar.timegm(dateutil.parser.parse(request_data['ts']).timetuple()) )
    else:
        # no timestamp in query parameters, so assume the timestamp is now.
        ts = int(time.time())

    # Get the value from the request
    val = request_data['val']

    # Convert/transform the fields for storage.
    ts, reading_id, val = convert_val(ts, reading_id, val, db)
    
    # The transformed value could be None, but the database insert method
    # will ignore it.
    msg = db.insert_reading(ts, reading_id, val)
    db.close()
    return msg

def store_many(req_data):
    """Stores a list of readings into the database.  'req_data' is a dictionary
    holding the reading information.  Currently, the 'format' item in 'req_data'
    determines the format of the data:

    'format' key not present: Format used by the Mini-Monitor
    'format' = 'monnit': format used by Webhooks generated by the iMonnit
    server used by Monnit wireless sensors.
    'format' = 'particle': format used by Webhook calls generated by Particle
    Photon and Electron devices.

    Returns the message returned by the database insert method.
    """

    # open the reading database 
    db = bmsdata.BMSdata()

    ts_lst = []
    reading_id_lst = []
    val_lst = []

    if not ('format' in req_data):
        # No 'format' key present.  This is conventional Mini-Monitor style data
        # The 'req_data' key 'readings' is a list of 3-element tuples. The three
        # elements of the tuple are:
        #     1:  Unix timestamp of the reading.
        #         If None, the current time is substituted.
        #     2:  The reading id.
        #     3:  The reading value.  convert_val() is used to convert/transform
        #         the value before storage.

        for ts, reading_id, val in req_data['readings']:
            try:
                ts = int(ts) if ts is not None else int(time.time())

                # Convert/transform the fields for storage.
                ts, reading_id, val = convert_val(ts, reading_id, val, db)
                ts_lst.append(ts)
                reading_id_lst.append(reading_id)
                val_lst.append(val)  # could be None, but insert_reading() will ignore it
            except Exception as e:
                _logger.exception('Error storing %s, %s, %s' % (ts, reading_id, val))

    elif req_data['format'] == 'monnit':
        # This is the fomrat used my Monnit Webhooks.  See documentation at:
        # https://www.imonnit.com/API/webhook.

        if 'sensorMessages' in req_data:
            # loop through and insert all of the sensor readings present in the
            # data payload
            for reading in req_data['sensorMessages']:
                try:
                    ts = int(calendar.timegm(dateutil.parser.parse(reading['messageDate']).timetuple()))

                    # sometimes multiple plot values are encoded by separating with the pipe character
                    # This happens with the CO sensor and the two channel relay.  Use the first value.
                    val = reading['plotValues'].split('|')[0]

                    reading_id = reading['sensorID']

                    # apply any requested conversions
                    ts, reading_id, val = convert_val(ts, reading_id, val, db)

                    ts_lst.append(ts)
                    val_lst.append(val)
                    reading_id_lst.append(reading_id)

                except Exception as e:
                    _logger.exception('Error storing %s' % reading)

    elif req_data['format'] == 'particle':
        # data from a Particle device, such as a Photon or Electron.  The important
        # keys in 'req_data' are:
        #    'coreid': This is the Device ID of the Photon/Electron and it is used as
        #              the base part of the BMON Sensor ID.
        #    'published_at': This is a UTC Date/Time string with the format similar to
        #              2015-11-24T06:21:16.568Z.  This is the time that data was sent by
        #              the Particle device.
        #    'data': This field holds one or more sensor readings and their associated
        #              variable names.  An example is: 'T1=73.2 T2=73.3 T3=73.2a a=300'
        #              Spaces separate readings.  Each reading is of the format
        #              [variable name]=[value], and the character 'a' may be appended, as
        #              in the variable T3 in the example.  The BMON Sensor ID is created by
        #              concatenating the 'coreid' value and the variable name, with an intervening
        #              underscore.  The BMON value comes direct from the 'value' portion above.
        #              The timestamp for the reading is the 'published_at' time from above, *except*
        #              if an 'a' is appended to the value.  In that case the 'published_at' time is 
        #              adjusted backward in time by the amount of seconds given in the 'a=XXX' item
        #              in the data string.  In this example, 300 seconds will be substracted from
        #              the 'published_at' timestamp for the T3 value above.  This feature is useful
        #              when the sensor value is an average of sensor readings across a period; in that
        #              case, the most accurate timestamp for the sensor reading is the midpoint of the
        #              period.  The 'a' adjustment can be used to produce this midpoint timestamp.

        # get the timestamp and convert to UNIX epoch format.
        ts_base = int( calendar.timegm(dateutil.parser.parse(req_data['published_at']).timetuple()) )

        # get the base for the sensor id, which is the coreid of the Particle board
        base_id = req_data['coreid']

        # break the data string into a dictionary with both the keys and values being strings
        data = {}
        for it in req_data['data'].split():
            ky, val = it.strip().split('=')
            data[ky] = val

        # A time adjustment value appears with a key of 'a'.  If present, take it out of the
        # data.
        ts_adj = data.get('a', 0)   # use 0 as default adjustment
        ts_adj = int(float(ts_adj))   # make an integer time adjustment
        if 'a' in data:
            del(data['a'])   # delete it out of the data dictionary

        # loop through the variables, preparing them for insertion
        for ky in list(data.keys()):
            reading_id = '%s_%s' % (base_id, ky)
            val = data[ky]
            try:
                if val[-1]=='a':
                    # use an adjusted time
                    ts = ts_base - ts_adj
                    val = float(val[:-1])
                else:
                    ts = ts_base
                    val = float(val)

                # Convert/transform the fields for storage.
                ts, reading_id, val = convert_val(ts, reading_id, val, db)
                ts_lst.append(ts)
                reading_id_lst.append(reading_id)
                val_lst.append(val)  # could be None, but insert_reading() will ignore it

            except Exception as e:
                _logger.exception('Error storing %s, %s' % (reading_id, val))

    # insert the readings into the database
    msg = db.insert_reading(ts_lst, reading_id_lst, val_lst)
    db.close()

    return msg
