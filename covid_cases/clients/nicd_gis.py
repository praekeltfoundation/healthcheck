from functools import lru_cache

import requests


class NICDGISClient:
    def __init__(self):
        self.session = requests.Session()

    @lru_cache()
    def get_ward_cases_data(self) -> dict:
        with self.session as session:
            response = session.get(
                url="https://gis.nicd.ac.za/hosting/rest/services/WARDS_MN/MapServer/0/query",
                params={
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "false",
                    "f": "json",
                },
                headers={"User-Agent": "contactndoh-whatsapp"},
                timeout=50,
            )
            response.raise_for_status()
            return response.json()

    def get_total_cases(self) -> int:
        api_data = self.get_ward_cases_data()
        total_cases = 0
        for record in api_data["features"]:
            total_cases += record["attributes"]["Tot_No_of_Cases"]
        return total_cases
