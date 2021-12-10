from dataclasses import dataclass
from typing import Dict

import requests
from bs4 import BeautifulSoup


@dataclass
class Counters:
    tests: int
    positive: int
    recoveries: int
    deaths: int
    vaccines: int


class SACoronavirusClient:
    def __init__(self):
        self.session = requests.Session()

    def get_homepage(self) -> str:
        with self.session as session:
            response = session.get(
                "https://sacoronavirus.co.za/",
                headers={"User-Agent": "contactndoh-whatsapp"},
                timeout=30,
            )
            response.raise_for_status()
            return response.text

    def get_homepage_counters(self) -> Counters:
        soup = BeautifulSoup(self.get_homepage(), "html.parser")
        counters = soup.find("div", class_="counters-box")
        for counter in counters.find_all("div", "counter-box-container"):
            name = counter.find("div", "counter-box-content").string
            if "test" in name.lower():
                tests = int(counter.span["data-value"])
            elif "case" in name.lower():
                positive = int(counter.span["data-value"])
            elif "recover" in name.lower():
                recoveries = int(counter.span["data-value"])
            elif "death" in name.lower():
                deaths = int(counter.span["data-value"])
            elif "vaccine" in name.lower():
                vaccines = int(counter.span["data-value"])
        return Counters(
            tests=tests,
            positive=positive,
            recoveries=recoveries,
            deaths=deaths,
            vaccines=vaccines,
        )
