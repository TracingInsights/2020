"""
Team Radio Download
===================
Downloads the team radio recordings (MP3) that F1 published for each 2020
session in its livetiming archive (TeamRadio.json of the session).

OpenF1, the source used by the 2023+ repos, has no data before 2023, so the
clips are listed from livetiming directly. Listing them requires the F1 TV
token that FastF1 uses (see README: "F1 TV authentication").

Output per session:
    {event_name}/{session_name}/{driver}/radio/{original_file_name}.mp3
    {event_name}/{session_name}/team_radio.json   (columnar index, sorted by time)

team_radio.json columns:
    drv   - driver abbreviation (e.g. "VER")
    dNum  - driver number as a string
    date  - UTC timestamp of the message (ISO 8601)
    file  - MP3 path relative to the session folder ("None" if download failed)
    url   - original recording URL on livetiming.formula1.com

  python team_radio.py                               # every event and session
  python team_radio.py --events "Monaco Grand Prix"  # one or more events
"""

import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import fastf1
import orjson
import pandas as pd
import requests
from fastf1._api import base_url as LIVETIMING_BASE_URL
from fastf1.req import Cache

logger = logging.getLogger("team_radio")

YEAR = 2020
EVENTS = [
    "Austrian Grand Prix",
    "Styrian Grand Prix",
    "Hungarian Grand Prix",
    "British Grand Prix",
    "70th Anniversary Grand Prix",
    "Spanish Grand Prix",
    "Belgian Grand Prix",
    "Italian Grand Prix",
    "Tuscan Grand Prix",
    "Russian Grand Prix",
    "Eifel Grand Prix",
    "Portuguese Grand Prix",
    "Emilia Romagna Grand Prix",
    "Turkish Grand Prix",
    "Bahrain Grand Prix",
    "Sakhir Grand Prix",
    "Abu Dhabi Grand Prix",
]
SESSIONS = ["Practice 1", "Practice 2", "Practice 3", "Qualifying", "Race"]

DOWNLOAD_WORKERS = 8
DOWNLOAD_RETRIES = 3
DOWNLOAD_TIMEOUT = 30

TEAM_RADIO_INDEX_KEYS = ("drv", "dNum", "date", "file", "url")


# ---------------------------------------------------------------------------
# Livetiming access
# ---------------------------------------------------------------------------


def fetch_team_radio(api_path: str) -> List[Dict[str, Any]]:
    """Return the session's radio captures as OpenF1-shaped entries.

    Entries have ``recording_url``, ``driver_number`` and ``date`` keys, the
    same shape OpenF1 returns, so the download/index code matches the 2023+
    repos. The request goes through FastF1, which adds the F1 TV token and
    caches the response.
    """
    session_url = f"{LIVETIMING_BASE_URL}{api_path}"
    response = Cache.requests_get(f"{session_url}TeamRadio.json")
    if response.status_code == 404:
        return []
    response.raise_for_status()
    captures = orjson.loads(response.content.decode("utf-8-sig")).get("Captures") or []
    if isinstance(captures, dict):  # keyframes may index captures by position
        captures = list(captures.values())

    entries = []
    seen = set()
    for capture in captures:
        path = capture.get("Path")
        # the feed occasionally repeats a capture; download each clip once
        if not path or path in seen:
            continue
        seen.add(path)
        number = capture.get("RacingNumber")
        date = pd.to_datetime(capture.get("Utc"), utc=True, errors="coerce")
        entries.append(
            {
                "recording_url": f"{session_url}{path}",
                "driver_number": int(number) if str(number).isdigit() else number,
                "date": None if pd.isna(date) else date.isoformat(timespec="microseconds"),
            }
        )
    return entries


def _session_drivers(base_dir: str) -> List[Dict[str, Any]]:
    """Entries of the session's drivers.json (empty if the session has no data)."""
    try:
        with open(os.path.join(base_dir, "drivers.json"), "rb") as f:
            return orjson.loads(f.read()).get("drivers", [])
    except (OSError, ValueError):
        return []


def _driver_codes(drivers: List[Dict[str, Any]], api_path: str) -> Dict[int, str]:
    """Driver number -> abbreviation, so clips land in the driver folders.

    Taken from drivers.json; entries written by older extractions have no
    driver number (``dn``), so the session's livetiming DriverList is used.
    """
    codes = {
        int(d["dn"]): d["driver"]
        for d in drivers
        if str(d.get("dn", "")).isdigit() and d.get("driver")
    }
    if codes:
        return codes
    response = Cache.requests_get(f"{LIVETIMING_BASE_URL}{api_path}DriverList.json")
    response.raise_for_status()
    driver_list = orjson.loads(response.content.decode("utf-8-sig"))
    return {
        int(number): info["Tla"]
        for number, info in driver_list.items()
        if str(number).isdigit() and isinstance(info, dict) and info.get("Tla")
    }


# ---------------------------------------------------------------------------
# Download & index
# ---------------------------------------------------------------------------


def _download_file(http: requests.Session, url: str, dest: str) -> bool:
    if os.path.isfile(dest) and os.path.getsize(dest) > 0:
        return True
    tmp = dest + ".part"
    for attempt in range(DOWNLOAD_RETRIES):
        try:
            with http.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True) as response:
                if response.status_code == 404:
                    logger.warning("Team radio not found: %s", url)
                    return False
                response.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        f.write(chunk)
            if os.path.getsize(tmp) == 0:
                raise requests.exceptions.RequestException("empty response")
            os.replace(tmp, dest)
            return True
        except (requests.exceptions.RequestException, OSError) as exc:
            logger.warning(
                "Team radio download failed (%d/%d) %s: %s",
                attempt + 1,
                DOWNLOAD_RETRIES,
                url,
                exc,
            )
            if attempt < DOWNLOAD_RETRIES - 1:
                time.sleep(0.5 * (2**attempt))
    if os.path.exists(tmp):
        os.remove(tmp)
    return False


def _driver_code(
    entry: Dict[str, Any], file_name: str, driver_codes: Optional[Dict[int, str]]
) -> str:
    number = entry.get("driver_number")
    if driver_codes and number in driver_codes and driver_codes[number]:
        return str(driver_codes[number])
    # Livetiming file names look like "VER_1_20261011_195602.mp3".
    prefix = file_name.split("_", 1)[0]
    if prefix.isalpha() and len(prefix) == 3:
        return prefix.upper()
    return str(number)


def save_session_radios(
    entries: List[Dict[str, Any]],
    base_dir: str,
    driver_codes: Optional[Dict[int, str]] = None,
    http: Optional[requests.Session] = None,
) -> Dict[str, list]:
    """Download radio MP3s for one session and write team_radio.json.

    ``driver_codes`` maps driver number -> abbreviation so files land in the
    same driver folders as the rest of the session data. Existing files are
    skipped, so re-running only fetches new clips.
    """
    entries = [e for e in entries if e.get("recording_url")]
    entries.sort(key=lambda e: str(e.get("date") or ""))

    index: Dict[str, list] = {k: [] for k in TEAM_RADIO_INDEX_KEYS}
    if not entries:
        return index

    os.makedirs(base_dir, exist_ok=True)
    http = http or requests.Session()

    jobs = []
    for entry in entries:
        url = entry["recording_url"]
        file_name = os.path.basename(urlparse(url).path) or "radio.mp3"
        code = _driver_code(entry, file_name, driver_codes)
        rel_path = f"{code}/radio/{file_name}"
        os.makedirs(os.path.join(base_dir, code, "radio"), exist_ok=True)
        jobs.append((entry, code, rel_path, url))

    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
        results = list(
            pool.map(
                lambda job: _download_file(
                    http, job[3], os.path.join(base_dir, job[2])
                ),
                jobs,
            )
        )

    for (entry, code, rel_path, url), ok in zip(jobs, results):
        number = entry.get("driver_number")
        index["drv"].append(code)
        index["dNum"].append(str(number) if number is not None else "None")
        index["date"].append(str(entry.get("date") or "None"))
        index["file"].append(rel_path if ok else "None")
        index["url"].append(url)

    with open(os.path.join(base_dir, "team_radio.json"), "wb") as f:
        f.write(orjson.dumps(index))

    failed = results.count(False)
    logger.info(
        "%s: %d team radio clips saved%s",
        base_dir,
        len(results) - failed,
        f", {failed} failed" if failed else "",
    )
    return index


# ---------------------------------------------------------------------------
# Season backfill
# ---------------------------------------------------------------------------


def download_season_radios(events: List[str], sessions: List[str]) -> int:
    http = requests.Session()
    failed = 0
    for event_name in events:
        for session_name in sessions:
            base_dir = f"{event_name}/{session_name}"
            drivers = _session_drivers(base_dir)
            if not drivers:
                # e.g. 2020 Styrian GP Practice 3, cancelled for rain
                logger.info("%s: no session data in the repo, skipped", base_dir)
                continue
            try:
                api_path = fastf1.get_session(YEAR, event_name, session_name).api_path
                driver_codes = _driver_codes(drivers, api_path)
                entries = fetch_team_radio(api_path)
            except Exception as exc:
                logger.error("%s: could not list team radio: %s", base_dir, exc)
                failed += 1
                continue
            if not entries:
                logger.info("%s: no team radio available", base_dir)
                continue
            index = save_session_radios(entries, base_dir, driver_codes, http)
            failed += index["file"].count("None")
    return failed


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger("fastf1").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--events", nargs="+", default=EVENTS)
    parser.add_argument("--sessions", nargs="+", default=SESSIONS)
    args = parser.parse_args()

    os.makedirs("cache", exist_ok=True)
    fastf1.Cache.enable_cache("cache")

    failed = download_season_radios(args.events, args.sessions)
    if failed:
        logger.error("%d team radio download(s) failed", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
