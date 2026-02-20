import requests
from typing import List
from pydantic import BaseModel


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


class POISearchInput(BaseModel):
    city: str
    interests: List[str]
    max_results: int = 20


class POISearchOutput(BaseModel):
    poi_id: str
    name: str
    category: str
    lat: float
    lon: float
    suggested_duration: int
    indoor: bool
    source: str


INTEREST_TO_OSM_TAG = {
    "history": '["tourism"="museum"]',
    "culture": '["amenity"="place_of_worship"]',
    "food": '["amenity"="restaurant"]',
    "nature": '["leisure"="park"]'
}


def search_pois(input_data: POISearchInput) -> List[POISearchOutput]:

    if input_data.city.lower() != "delhi":
        raise ValueError("Currently only Delhi is supported.")

    tag_queries = []
    for interest in input_data.interests:
        if interest in INTEREST_TO_OSM_TAG:
            tag_queries.append(f'node{INTEREST_TO_OSM_TAG[interest]}(area.searchArea);')

    if not tag_queries:
        return []

    overpass_query = f"""
    [out:json];
    area["name"="Delhi"]->.searchArea;
    (
        {"".join(tag_queries)}
    );
    out center {input_data.max_results};
    """

    response = requests.post(OVERPASS_URL, data={"data": overpass_query})
    data = response.json()

    results = []

    for element in data.get("elements", [])[: input_data.max_results]:
        name = element.get("tags", {}).get("name")
        if not name:
            continue

        category = list(element.get("tags", {}).values())[0]

        results.append(
            POISearchOutput(
                poi_id=f"osm_{element['id']}",
                name=name,
                category=category,
                lat=element.get("lat"),
                lon=element.get("lon"),
                suggested_duration=90,
                indoor=False,
                source="OpenStreetMap"
            )
        )

    return results