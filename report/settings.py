import logging as log
import uuid

log.basicConfig(filename='report.log', encoding='utf-8', level=log.DEBUG)

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
    'AssestByVulnerabilities': {
        'page': 1,
        'crop': (108,252,1677,621)
    }
}