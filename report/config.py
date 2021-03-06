import logging as log
import uuid, os, json

BASIC_SETTINGS = {
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
    'api': {
        'single_fetch_size': 10,
        'max_wait_time': 10,
        'endpoint': 'https://console.rapid7.aws.assaabloy.net/api/3',
        'list': '/reports?size=$SIZE&page=$PAGE&sort=id,asc',
        'generate': '/reports/$ID/generate',
        'instance_history': '/reports/$ID/history/$INSTANCE',
        'download': '/reports/$ID/history/$INSTANCE/output'
    },
    'log': {
        'name': 'report.log',
        'level': 'DEBUG',
        'format': '%(asctime)s | %(module)s | %(funcName)s | %(lineno)d | %(levelname)s | %(message)s'
    },
    'autoprocess': [
        'AAES - Top 10 Assets by Vurlnerabilities - External',
        'AAES - Top 10 Assets by Vurlnerabilities',
        'AAES - TOP25 Remediation with Details',
        'AAGC - Top 10 Assets by Vurlnerabilities',
        'AAGC - TOP25 Remediation with Details',
        'AAGS - Top 10 Assets by Vurlnerabilities - External',
        'AAGS - Top 10 Assets by Vurlnerabilities',
        'AAGS - TOP25 Remediation with Details',
        'AAGT - Top 10 Assets by Vurlnerabilities',
        'AAGT - TOP25 Remediation with Details',
        'AMER - Top 10 Assets by Vurlnerabilities - External',
        'AMER - Top 10 Assets by Vurlnerabilities',
        'AMER - TOP25 Remediation with Details',
        'APAC - Top 10 Assets by Vurlnerabilities',
        'APAC TOP25 Remediation with Details',
        'APAC- Top 10 Assets by Vurlnerabilities - External',
        'EMEA - Top 10 Assets by Vurlnerabilities - External',
        'EMEA - Top 10 Assets by Vurlnerabilities',
        'EMEA - TOP25 Remediation with Details',
        'GSSC - Top 10 Assets by Vurlnerabilities - External',
        'GSSC - Top 10 Assets by Vurlnerabilities',
        'GSSC - TOP25 Remediation with Details',
        'HIDG - Top 10 Assets by Vurlnerabilities - External',
        'HIDG - Top 10 Assets by Vurlnerabilities',
        'HIDG - TOP25 Remediation with Details']}
class Settings:
    def __init__(self, path:str=None):
        self.dir = path or os.path.dirname(__file__)
        self.path = os.path.join(self.dir, 'settings.json')
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                self.settings = json.load(file)
        else:
            self.settings = BASIC_SETTINGS

    def save(self):
        if os.path.exists(self.path):
            with open(self.path, 'w') as file:
                json.dump(self.settings, file, indent=4)
        else:
            with open(self.path, 'x') as file:
                json.dump(self.settings, file, indent=4)

    def __getattr__(self, scope):
        return self.settings[scope]


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


SETTINGS = Settings()

LOG_LEVEL = {
    'NONE': log.NOTSET,
    'DEBUG': log.DEBUG,
    'INFO': log.INFO,
    'WARNING': log.WARNING,
    'ERROR': log.ERROR,
    'CRITICAL': log.CRITICAL
}

log.basicConfig(
    filename=os.path.join(SETTINGS.dir, SETTINGS.log['name']),
    level=LOG_LEVEL[SETTINGS.log['level']],
    format=SETTINGS.log['format'],
    encoding='utf-8'
)



