import requests
from typing import Dict, Any, Optional

TELETRAC_API_KEY = "9e8799b0306c48f3b30f2445ac0a0156"
BASE_URL = "https://director-au.teletracnavman.net/api/v1/"


def get_trip_history(vehicle_id: str, params: Optional[Dict[str, Any]] = None) -> Dict:
    url = f"{BASE_URL}vehicles/{vehicle_id}/triphistory"
    headers = {"Authorization": f"Bearer {TELETRAC_API_KEY}"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_alerts(params: Optional[Dict[str, Any]] = None) -> Dict:
    url = f"{BASE_URL}alerts"
    headers = {"Authorization": f"Bearer {TELETRAC_API_KEY}"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_vehicles() -> Dict:
    url = f"{BASE_URL}vehicles"
    headers = {"Authorization": f"Bearer {TELETRAC_API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
