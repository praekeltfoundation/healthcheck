import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterator

import requests
from bs4 import BeautifulSoup


@dataclass
class Counters:
    tests: int
    positive: int
    recoveries: int
    deaths: int
    vaccines: int


@dataclass
class CaseImage:
    url: str
    date: date


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

    def get_daily_cases_page(self) -> str:
        with self.session as session:
            response = session.get(
                "https://sacoronavirus.co.za/category/daily-cases",
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

    def get_daily_cases_image_urls(self) -> Iterator[CaseImage]:
        soup = BeautifulSoup(self.get_daily_cases_page(), "html.parser")
        for article in soup.main.find_all("article"):
            url = article.img["src"]
            d = article.select("h2.entry-title")[0].string
            d = re.search(".*\((.*)\).*", d).group(1)
            d = datetime.strptime(d, "%A %d %B %Y").date()
            yield CaseImage(url=url, date=d)
