import logging as log
import uuid, os

LOG_LEVEL = {
    'NONE': log.NOTSET,
    'DEBUG': log.DEBUG,
    'INFO': log.INFO,
    'WARNING': log.WARNING,
    'ERROR': log.ERROR,
    'CRITICAL': log.CRITICAL
}

CONFIG = {
    'zoom': {
        'x': 3,
        'y': 3
    },
    'rotate': 0,
    'format': 'png',
    'filename': uuid.uuid4,
    'path': './scan',
    'colorspace': 'RGB',
    'separate_by_regions': False,
    'region_code_pattern': r"(?P<region>[A-Z]{4})",
    'naming_pattern': r"((?P<region>[A-Z]{4})([-\s])*)?(?P<type>[0-9a-zA-Z\s-]+)\.(pdf|PDF)"
}

BASE_SETTINGS = {
    'scanner': {
        'Top25': {
            'page': 1,
            'crop': (108,252,1677,621)
        },
        'Top10': {
            'page': 1,
            'crop': (73,73,1720,1040)
        }
    },
    'pdf': {
        "Top 10 Assets by Vurlnerabilities - External": 'Top10',
        "Top 10 Assets by Vurlnerabilities": 'Top10',
        "TOP25 Remediation with Details": 'Top25'
    },
    'discovery': {
        'prioritize_filename_regions': True
    },
    'rapid': {
        'single_fetch_size': 10,
        'endpoint': 'https://console.rapid7.aws.assaabloy.net/api/3/',
        'list': 'reports?size=$SIZE&page=$PAGE&sort=id,asc'
    }
}

class Settings:
    def __init__(self):pass

print(__file__)
         