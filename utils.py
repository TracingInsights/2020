import json
import logging
import math
from typing import Any, Dict, List, Optional

import requests
from fastf1.mvapi.api import get_circuit

logger = logging.getLogger(__name__)

# Circuit section breakdowns live in sections/<circuit>.json (percentages of
# the lap distance). Each 2020 event is mapped explicitly to its file; there
# is no fuzzy matching on event or circuit names. Events without an entry get
# no sections, either because there is no sections file for the circuit
# (Tuscan: Mugello, Russian: Sochi, Eifel: Nurburgring, Portuguese: Portimao,
# Turkish: Istanbul Park) or because the 2020 layout differs from the one the
# file describes, so its percentages would misplace the sections (Spanish:
# final chicane removed 2023; Sakhir: Bahrain Outer Circuit; Abu Dhabi:
# reprofiled 2021).
# Event name -> sections/ file name (without the .json extension).
EVENT_SECTIONS_FILE: Dict[str, str] = {
    "Austrian Grand Prix": "red-bull-ring",
    "Styrian Grand Prix": "red-bull-ring",
    "Hungarian Grand Prix": "hungary",
    "British Grand Prix": "silverstone",
    "70th Anniversary Grand Prix": "silverstone",
    "Belgian Grand Prix": "circuit-de-spa-francorchamps",
    "Italian Grand Prix": "monza",
    "Emilia Romagna Grand Prix": "emilia",
    "Bahrain Grand Prix": "bahrain-international-circuit",
}

def get_events(year):
    events = {
        2024: [
            "Pre-Season Testing",
            "Bahrain Grand Prix",
            "Saudi Arabian Grand Prix",
            "Australian Grand Prix",
            "Japanese Grand Prix",
            "Chinese Grand Prix",
            "Miami Grand Prix",
            "Emilia Romagna Grand Prix",
            "Monaco Grand Prix",
            "Canadian Grand Prix",
            "Spanish Grand Prix",
            "Austrian Grand Prix",
            "British Grand Prix",
            "Hungarian Grand Prix",
            "Belgian Grand Prix",
            "Dutch Grand Prix",
            "Italian Grand Prix",
            "Azerbaijan Grand Prix",
            "Singapore Grand Prix",
            "United States Grand Prix",
            "Mexico City Grand Prix",
            "São Paulo Grand Prix",
            "Las Vegas Grand Prix",
            "Qatar Grand Prix",
            "Abu Dhabi Grand Prix",
        ],
        2023: [
            "Abu Dhabi Grand Prix",
            "Las Vegas Grand Prix",
            "São Paulo Grand Prix",
            "Mexico City Grand Prix",
            "United States Grand Prix",
            "Qatar Grand Prix",
            "Japanese Grand Prix",
            "Singapore Grand Prix",
            "Italian Grand Prix",
            "Dutch Grand Prix",
            "Belgian Grand Prix",
            "Hungarian Grand Prix",
            "British Grand Prix",
            "Austrian Grand Prix",
            "Canadian Grand Prix",
            "Spanish Grand Prix",
            "Monaco Grand Prix",
            "Miami Grand Prix",
            "Azerbaijan Grand Prix",
            "Australian Grand Prix",
            "Saudi Arabian Grand Prix",
            "Bahrain Grand Prix",
            "Pre-Season Testing",
        ],
        2022: [
            "Abu Dhabi Grand Prix",
            "São Paulo Grand Prix",
            "Mexico City Grand Prix",
            "United States Grand Prix",
            "Japanese Grand Prix",
            "Singapore Grand Prix",
            "Italian Grand Prix",
            "Dutch Grand Prix",
            "Belgian Grand Prix",
            "Hungarian Grand Prix",
            "French Grand Prix",
            "Austrian Grand Prix",
            "British Grand Prix",
            "Canadian Grand Prix",
            "Azerbaijan Grand Prix",
            "Monaco Grand Prix",
            "Spanish Grand Prix",
            "Miami Grand Prix",
            "Emilia Romagna Grand Prix",
            "Australian Grand Prix",
            "Saudi Arabian Grand Prix",
            "Bahrain Grand Prix",
            "Pre-Season Test",
        ],
        2021: [
            "Abu Dhabi Grand Prix",
            "Saudi Arabian Grand Prix",
            "Qatar Grand Prix",
            "São Paulo Grand Prix",
            "Mexico City Grand Prix",
            "United States Grand Prix",
            "Turkish Grand Prix",
            "Russian Grand Prix",
            "Italian Grand Prix",
            "Dutch Grand Prix",
            "Belgian Grand Prix",
            "Hungarian Grand Prix",
            "British Grand Prix",
            "Austrian Grand Prix",
            "Styrian Grand Prix",
            "French Grand Prix",
            "Azerbaijan Grand Prix",
            "Monaco Grand Prix",
            "Spanish Grand Prix",
            "Portuguese Grand Prix",
            "Emilia Romagna Grand Prix",
            "Bahrain Grand Prix",
        ],
        2020: [
            "Abu Dhabi Grand Prix",
            "Sakhir Grand Prix",
            "Bahrain Grand Prix",
            "Turkish Grand Prix",
            "Emilia Romagna Grand Prix",
            "Portuguese Grand Prix",
            "Eifel Grand Prix",
            "Russian Grand Prix",
            "Tuscan Grand Prix",
            "Italian Grand Prix",
            "Belgian Grand Prix",
            "Spanish Grand Prix",
            "70th Anniversary Grand Prix",
            "British Grand Prix",
            "Hungarian Grand Prix",
            "Styrian Grand Prix",
            "Austrian Grand Prix",
        ],
        2019: [
            "Abu Dhabi Grand Prix",
            "Brazilian Grand Prix",
            "United States Grand Prix",
            "Mexican Grand Prix",
            "Japanese Grand Prix",
            "Russian Grand Prix",
            "Singapore Grand Prix",
            "Italian Grand Prix",
            "Belgian Grand Prix",
            "Hungarian Grand Prix",
            "German Grand Prix",
            "British Grand Prix",
            "Austrian Grand Prix",
            "French Grand Prix",
            "Canadian Grand Prix",
            "Monaco Grand Prix",
            "Spanish Grand Prix",
            "Azerbaijan Grand Prix",
            "Chinese Grand Prix",
            "Bahrain Grand Prix",
            "Australian Grand Prix",
        ],
        2018: [
            "Abu Dhabi Grand Prix",
            "Brazilian Grand Prix",
            "Mexican Grand Prix",
            "United States Grand Prix",
            "Japanese Grand Prix",
            "Russian Grand Prix",
            "Singapore Grand Prix",
            "Italian Grand Prix",
            "Belgian Grand Prix",
            "Hungarian Grand Prix",
            "German Grand Prix",
            "British Grand Prix",
            "Austrian Grand Prix",
            "French Grand Prix",
            "Canadian Grand Prix",
            "Monaco Grand Prix",
            "Spanish Grand Prix",
            "Azerbaijan Grand Prix",
            "Chinese Grand Prix",
            "Bahrain Grand Prix",
            "Australian Grand Prix",
        ],
    }

    return events.get(year, [])


def get_sessions(year, event):
    p1_p2_p3 = ["Practice 1", "Practice 2", "Practice 3"]
    p1_p2_q_r = ["Practice 1", "Practice 2", "Qualifying", "Race"]
    p2_p3_q_r = ["Practice 2", "Practice 3", "Qualifying", "Race"]
    p3_q_r = ["Practice 3", "Qualifying", "Race"]
    p1_q_r = ["Practice 1", "Qualifying", "Race"]
    normal_sessions = [
        "Practice 1",
        "Practice 2",
        "Practice 3",
        "Qualifying",
        "Race",
    ]

    normal_sprint = [
        "Practice 1",
        "Qualifying",
        "Practice 2",
        "Sprint Qualifying",
        "Race",
    ]
    sprint_2022 = [
        "Practice 1",
        "Qualifying",
        "Practice 2",
        "Sprint",
        "Race",
    ]

    sprint_shootout = [
        "Practice 1",
        "Qualifying",
        "Sprint Shootout",
        "Sprint",
        "Race",
    ]
    sprint_shootout_2024 = [
        "Practice 1",
        "Sprint Shootout",
        "Sprint",
        "Qualifying",
        "Race",
    ]

    if year == 2018:
        return normal_sessions
    if year == 2019:
        if event == "Japanese Grand Prix":
            return p1_p2_q_r
        return normal_sessions
    if year == 2020:
        if event == "Styrian Grand Prix":
            return p1_p2_q_r
        if event == "Eifel Grand Prix":
            return p3_q_r
        if event == "Emilia Romagna Grand Prix":
            return p1_q_r

        return normal_sessions
    if year == 2021:
        if (
            event == "British Grand Prix"
            or event == "Italian Grand Prix"
            or event == "São Paulo Grand Prix"
        ):
            return normal_sprint
        else:
            return normal_sessions

    if year == 2022:
        if event == "Pre-Season Test":
            return p1_p2_p3
        if (
            event == "Austrian Grand Prix"
            or event == "Emilia Romagna Grand Prix"
            or event == "São Paulo Grand Prix"
        ):
            return sprint_2022
        else:
            return normal_sessions

    if year == 2023:
        if event == "Pre-Season Testing":
            return p1_p2_p3
        if event == "Hungarian Grand Prix":
            return p2_p3_q_r
        if (
            event == "Austrian Grand Prix"
            or event == "Azerbaijan Grand Prix"
            or event == "Belgium Grand Prix"
            or event == "Qatar Grand Prix"
            or event == "United States Grand Prix"
            or event == "São Paulo Grand Prix"
        ):
            return sprint_shootout
        else:
            return normal_sessions
    if year == 2024:
        if event == "Pre-Season Testing":
            return p1_p2_p3
        if (
            event == "Chinese Grand Prix"
            or event == "Miami Grand Prix"
            or event == "Austrian Grand Prix"
            or event == "United States Grand Prix"
            or event == "São Paulo Grand Prix"
            or event == "Qatar Grand Prix"
        ):
            return sprint_shootout_2024

        return normal_sessions

# make sure that year can be from 2018 to current year
class LatestData:
    def __init__(self, year):
        self.year = year
        self.data = self.get_f1_data()
        self.events = self.get_events()

    def get_f1_data(self):
        response = requests.get(
            f"https://livetiming.formula1.com/static/{self.year}/Index.json", timeout=5
        )
        if response.status_code == 200:
            try:
                data = response.content.decode("utf-8-sig")
                return json.loads(data)
            except json.JSONDecodeError as e:
                print("Failed to parse JSON data:", e)
                return None
        else:
            print("Failed to get data. Status code:", response.status_code)
            return None

    def get_events(self):
        events = []
        for meeting in self.data["Meetings"]:
            events.append(meeting["Name"])

        return events

    def get_sessions(self, event):
        sessions = []
        for meeting in self.data["Meetings"]:
            if meeting["Name"] == event:
                for session in meeting["Sessions"]:
                    sessions.append(session["Name"])

        return sessions


def team_colors(year: int) -> dict:
    team_colors = {}

    if year == 2023:
        team_colors = {
            "Red Bull Racing": "#ffe119",
            "Ferrari": "#e6194b",
            "Aston Martin": "#3cb44b",
            "Mercedes": "#00c0bf",
            "Alpine": "#f032e6",
            "Haas F1 Team": "#ffffff",
            "McLaren": "#f58231",
            "Alfa Romeo": "#800000",
            "AlphaTauri": "#dcbeff",
            "Williams": "#4363d8",
            "Red Bull Racing Honda RBPT": "#ffe119",
            "Ferrari": "#e6194b",
            "Aston Martin Aramco Mercedes": "#3cb44b",
            "Mercedes": "#00c0bf",
            "Alpine Renault": "#f032e6",
            "Haas Ferrari": "#ffffff",
            "McLaren Mercedes": "#f58231",
            "Alfa Romeo Ferrari": "#800000",
            "AlphaTauri Honda RBPT": "#dcbeff",
            "Williams Mercedes": "#4363d8",
            "Red Bull": "#ffe119",
            "Alpine F1 Team": "#f032e6",
        }
    if year == 2022:
        team_colors = {
            "Red Bull Racing": "#ffe119",
            "Ferrari": "#e6194b",
            "Aston Martin": "#3cb44b",
            "Mercedes": "#00c0bf",
            "Alpine": "#f032e6",
            "Haas F1 Team": "#ffffff",
            "McLaren": "#f58231",
            "Alfa Romeo": "#800000",
            "AlphaTauri": "#dcbeff",
            "Williams": "#4363d8",
            "Red Bull": "#ffe119",
            "Alpine F1 Team": "#f032e6",
        }

    if year == 2021:
        team_colors = {
            "Red Bull Racing": "#ffe119",
            "Mercedes": "#00c0bf",
            "Ferrari": "#e6194b",
            "Alpine": "#f032e6",
            "McLaren": "#f58231",
            "Alfa Romeo Racing": "#800000",
            "Aston Martin": "#3cb44b",
            "Haas F1 Team": "#ffffff",
            "AlphaTauri": "#dcbeff",
            "Williams": "#4363d8",
            "Red Bull": "#ffe119",
            "Alpine F1 Team": "#f032e6",
            "Alfa Romeo": "#800000",
        }

    if year == 2020:
        team_colors = {
            "Red Bull Racing": "#000099",
            "Renault": "#ffe119",
            "Racing Point": "#f032e6",
            "Mercedes": "#00c0bf",
            "Ferrari": "#e6194b",
            "McLaren": "#f58231",
            "Alfa Romeo Racing": "#800000",
            "Haas F1 Team": "#ffffff",
            "AlphaTauri": "#dcbeff",
            "Williams": "#4363d8",
            "Red Bull": "#000099",
            "Alfa Romeo": "#800000",
        }

    if year == 2019:
        team_colors = {
            "Red Bull Racing": "#000099",
            "Renault": "#ffe119",
            "Racing Point": "#f032e6",
            "Toro Rosso": "#dcbeff",
            "Mercedes": "#00c0bf",
            "Ferrari": "#e6194b",
            "McLaren": "#f58231",
            "Alfa Romeo Racing": "#800000",
            "Haas F1 Team": "#ffffff",
            "Williams": "#4363d8",
            "Red Bull": "#000099",
            "Alfa Romeo": "#800000",
        }

    if year == 2018:
        team_colors = {
            "Red Bull Racing": "#000099",
            "Renault": "#ffe119",
            "Toro Rosso": "#dcbeff",
            "Force India": "#f032e6",
            "Sauber": "#800000",
            "Mercedes": "#00c0bf",
            "Ferrari": "#e6194b",
            "McLaren": "#f58231",
            "Haas F1 Team": "#ffffff",
            "Williams": "#4363d8",
            "Red Bull": "#000099",
        }

    return team_colors


# ---------------------------------------------------------------------------
# MultiViewer circuit details for corners.json
# ---------------------------------------------------------------------------

def _float_or_none(value: Any) -> Optional[float]:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _int_or_none(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _mv_distance(entry: Dict) -> Optional[float]:
    """MultiViewer's own marker distance from the start/finish line, in meters
    (the API's ``length`` is in decimeters)."""
    length = _float_or_none(entry.get("length"))
    return None if length is None else length / 10


def get_mv_circuit_payload(f1session) -> Optional[Dict]:
    """Raw MultiViewer circuit payload for the session's circuit.

    This is the same request ``Session.get_circuit_info()`` makes, so it is
    served from FastF1's HTTP cache. Returns None if the request fails, or if
    MultiViewer answers with a different circuit: F1 reuses circuit keys
    (2020 Mugello's key 149 is Jeddah from 2021), and MultiViewer then serves
    the newer circuit's layout, marshal positions and pit loss.
    """
    try:
        circuit = f1session.session_info["Meeting"]["Circuit"]
        payload = get_circuit(year=f1session.event.year, circuit_key=circuit["Key"])
    except Exception as e:
        logger.warning(f"Could not fetch MultiViewer circuit data: {e}")
        return None
    if not payload:
        return None
    name, year = payload.get("circuitName"), _int_or_none(payload.get("year"))
    if name != circuit.get("ShortName") or (
        year is not None and year > f1session.event.year
    ):
        logger.warning(
            f"Ignoring MultiViewer circuit data for {circuit.get('ShortName')}: "
            f"key {circuit['Key']} returned {name} ({year})"
        )
        return None
    return payload


def _marker_columns(
    prefix: str, entries: List[Dict], telemetry_distances: Optional[List]
) -> Dict[str, list]:
    mv_distances = [_mv_distance(e) for e in entries]
    return {
        f"{prefix}Number": [_int_or_none(e.get("number")) for e in entries],
        f"{prefix}X": [
            _float_or_none((e.get("trackPosition") or {}).get("x")) for e in entries
        ],
        f"{prefix}Y": [
            _float_or_none((e.get("trackPosition") or {}).get("y")) for e in entries
        ],
        f"{prefix}Angle": [_float_or_none(e.get("angle")) for e in entries],
        f"{prefix}Distance": (
            telemetry_distances if telemetry_distances is not None else mv_distances
        ),
        f"{prefix}MVDistance": mv_distances,
    }


def build_circuit_details(payload: Optional[Dict], circuit_info=None) -> Dict:
    """Extra corners.json fields from the raw MultiViewer circuit payload.

    Per-corner columns are aligned with ``CornerNumber`` (FastF1 builds its
    corner rows from the same payload, in the same order). ``circuit_info`` is
    the FastF1 CircuitInfo whose marshal ``Distance`` values were computed from
    the reference lap's telemetry; without it (API fallback path) marshal
    distances fall back to MultiViewer's own distance, as corners do there.
    """
    payload = payload or {}
    corners = payload.get("corners") or []
    letters = [str(c.get("letter") or "") for c in corners]
    pit_loss = payload.get("pitLoss") or {}
    lap = payload.get("candidateLap") or {}

    def telemetry_distances(df) -> Optional[List]:
        if df is None:
            return None
        return [_float_or_none(v) for v in df["Distance"]]

    lights_df = circuit_info.marshal_lights if circuit_info is not None else None
    sectors_df = circuit_info.marshal_sectors if circuit_info is not None else None

    return {
        "CornerLetter": letters,
        "CornerLabel": [
            f"{c.get('number', '')}{letter}" for c, letter in zip(corners, letters)
        ],
        "MVDistance": [_mv_distance(c) for c in corners],
        **_marker_columns(
            "MarshalLight",
            payload.get("marshalLights") or [],
            telemetry_distances(lights_df),
        ),
        **_marker_columns(
            "MarshalSector",
            payload.get("marshalSectors") or [],
            telemetry_distances(sectors_df),
        ),
        "CircuitKey": _int_or_none(payload.get("circuitKey")),
        "CircuitName": payload.get("circuitName"),
        "Location": payload.get("location"),
        "CountryName": payload.get("countryName"),
        "CountryKey": _int_or_none(payload.get("countryKey")),
        "CountryIocCode": payload.get("countryIocCode"),
        "PitLossNormal": _float_or_none(pit_loss.get("normal")),
        "PitLossSC": _float_or_none(pit_loss.get("sc")),
        "PitLossVSC": _float_or_none(pit_loss.get("vsc")),
        "LayoutYear": _int_or_none(payload.get("year")),
        "LayoutRound": _int_or_none(payload.get("round")),
        "LayoutRaceDate": payload.get("raceDate"),
        "LayoutMeetingKey": _int_or_none(payload.get("meetingKey")),
        "LayoutMeetingName": payload.get("meetingName"),
        "LayoutMeetingOfficialName": payload.get("meetingOfficialName"),
        "LayoutLapDriverNumber": lap.get("driverNumber"),
        "LayoutLapNumber": _int_or_none(lap.get("lapNumber")),
        "LayoutLapSession": lap.get("session"),
        "LayoutLapTime": _float_or_none(lap.get("lapTime")),
        "LayoutLapStartDate": lap.get("lapStartDate"),
        "LayoutLapStartSessionTime": _float_or_none(lap.get("lapStartSessionTime")),
        "LayoutLapSessionStartTime": _float_or_none(lap.get("sessionStartTime")),
        "TrackX": list(payload.get("x") or []),
        "TrackY": list(payload.get("y") or []),
        "TrackTime": list(payload.get("trackPositionTime") or []),
        "MiniSectorIndex": list(payload.get("miniSectorsIndexes") or []),
    }
