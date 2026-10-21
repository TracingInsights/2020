"""
Corners Backfill
================
Rewrites {event_name}/{session_name}/corners.json for every 2020 session
without re-extracting telemetry.

The output is identical to what the session scripts (FP1.py ... R.py) write:
FastF1 corner positions, the circuit's section breakdown (sections/, mapped in
utils.EVENT_SECTIONS_FILE) and the MultiViewer circuit details (marshal
lights/sectors, pit loss, layout lap, track outline).

  python corner.py                                   # every event and session
  python corner.py --events "Monaco Grand Prix"      # one or more events
  python corner.py --sessions Race Qualifying        # one or more sessions
"""

import argparse
import logging
import os

import fastf1
import orjson

from R import SeasonSessionExtractor, _write_json

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

logger = logging.getLogger("corner")


def write_session_corners(
    extractor: SeasonSessionExtractor, event_name: str, session_name: str
) -> bool:
    base_dir = f"{event_name}/{session_name}"
    try:
        with open(f"{base_dir}/drivers.json", "rb") as f:
            has_drivers = bool(orjson.loads(f.read()).get("drivers"))
    except (OSError, ValueError):
        has_drivers = False
    if not has_drivers:
        # e.g. 2020 Styrian GP Practice 3, cancelled for rain
        logger.info(f"Skipping {base_dir}: no session data in the repo")
        return False

    # Corners only need laps, car/position data and session info, so skip
    # weather and race control messages; seeding the extractor's session
    # cache makes get_circuit_info() reuse this lighter load.
    f1session = fastf1.get_session(YEAR, event_name, session_name)
    f1session.load(laps=True, telemetry=True, weather=False, messages=False)
    f1session._telemetry_loaded = True
    extractor._session_cache[f"{YEAR}-{event_name}-{session_name}"] = f1session

    try:
        corner_info = extractor.get_circuit_info(event_name, session_name)
    finally:
        extractor._session_cache.clear()
        extractor._circuit_cache.clear()

    if not corner_info:
        logger.error(f"✗ No corner data for {base_dir}")
        return False

    _write_json(f"{base_dir}/corners.json", corner_info)
    sections = len(corner_info.get("SectionType") or [])
    logger.info(
        f"✓ {base_dir}/corners.json "
        f"(layout year {corner_info.get('LayoutYear')}, "
        f"{f'{sections} sections' if sections else 'no sections'})"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--events", nargs="+", default=EVENTS)
    parser.add_argument("--sessions", nargs="+", default=SESSIONS)
    args = parser.parse_args()

    os.makedirs("cache", exist_ok=True)
    fastf1.Cache.enable_cache("cache")

    extractor = SeasonSessionExtractor(year=YEAR)
    failed = []
    for event_name in args.events:
        for session_name in args.sessions:
            try:
                write_session_corners(extractor, event_name, session_name)
            except Exception as e:
                logger.error(f"✗ {event_name}/{session_name}: {e}")
                failed.append(f"{event_name}/{session_name}")

    if failed:
        logger.error(f"{len(failed)} session(s) failed: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
