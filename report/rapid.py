from .settings import RAPID_REPORT_GENERATE, RAPID_REPORT_DOWNLOAD
import requests


class Rapid:

    def __init__(self, mail:str, password:str) -> None:
        self.auth = (mail, password)

    def generate(self, id) -> str:
        return requests.post(
            RAPID_REPORT_GENERATE.substitute(id=id),
            auth=self.auth)

    def download(self, id) -> str:
        return requests.get(
            RAPID_REPORT_DOWNLOAD.substitute(id=id),
            auth=self.auth)