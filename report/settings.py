import logging as log

log.basicConfig(filename='report.log', encoding='utf-8', level=log.DEBUG)

PDF2IMG_EXPORT_PRESETS = {
    'AssestByVulnerabilities': {
        'page': 1,
        'start': (0,0),
        'end': (100,100)
    }
}
