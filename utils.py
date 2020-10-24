import datetime
import logging

def benchmark(msg, f, *args):
        start = datetime.datetime.now()
        result = f(*args)
        elapsed = datetime.datetime.now() - start
        if(msg is not None):
            logging.info(msg.format(hhmmssms_from_ms(elapsed.total_seconds() * 1000)))

        return result

def parse_boolean(value):
    if(value is None):
        return None
    elif (value == 'Yes'):
        return True
    
    return False

def key_from_dict_query(dict):
    return dict['query'] + ', '.join(dict['params'])

def is_none(value):
    return value is None or value == 'NONE'

def upper(value):
    if(value is None):
        return None

    return str(value).upper().strip()

def hhmmssms_from_ms(value):
    milliseconds = (int) (value % 1000)
    seconds = (int) ((value / 1000) % 60)
    minutes = (int) (((value / 1000) / 60) % 60)
    hours = (int) ((((value / 1000) / 60) / 60) % 24)

    return '{:02d}:{:02d}:{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)