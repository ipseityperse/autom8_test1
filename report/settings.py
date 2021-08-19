import logging as log
import uuid
from string import Template


log.basicConfig(filename='report.log', encoding='utf-8', level=log.DEBUG,
                format='%(asctime)s | %(module)s | %(funcName)s | %(lineno)d | %(levelname)s | %(message)s')

SCANNER_DEFAULTS = {
    'zoom': {
        'x': 3,
        'y': 3
    },
    'rotate': 0,
    'output_image_format': 'png',
    'output_image_filename': uuid.uuid4,
    'output_image_path': './scan',
    'colorspace': 'RGB'
}

PDF2IMG_EXPORT_PRESETS = {
    'Top25': {
        'page': 1,
        'crop': (108,252,1677,621)
    },
    'Top10': {
        'page': 1,
        'crop': (73,73,1720,1040)
    }
}

# EXAMPLE: AMER - Top 10 Assets by Vurlnerabilities - External.pdf
PDF_NAMING_PATTERN = r"((?P<region>[A-Z]{4})([-\s])*)?(?P<type>[0-9a-zA-Z\s-]+)\.(pdf|PDF)"
REGION_CODE_PATTERN = r"(?P<region>[A-Z]{4})"

PREFER_FILENAME_REGION_CODES = True

PDF_REPORT_TYPES = {
    "Top 10 Assets by Vurlnerabilities - External": 'Top10',
    "Top 10 Assets by Vurlnerabilities": 'Top10',
    "TOP25 Remediation with Details": 'Top25'
}

FLAT, REGION_FOLDERS = False, True
SCANNER_OUTPUT_IN_FOLDERS = FLAT

RAPID_REPORT_API = 'https://console.rapid7.aws.assaabloy.net/api/3/reports/'
RAPID_REPORT_INSTANCE = 'latest'
RAPID_REPORT_GENERATE = Template(f'{RAPID_REPORT_API}$id/generate')
RAPID_REPORT_DOWNLOAD = Template(f'{RAPID_REPORT_API}$id/history/{RAPID_REPORT_INSTANCE}/output')

THREADS = 10