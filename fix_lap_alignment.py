"""Repair lap numbering for a race where F1's timing feed dropped laps.

FastF1 builds lap boundaries by chaining lap times. When the TimingData feed
misses some laps (2020 Austrian GP Race: ~5 laps around laps 9-13), FastF1
numbers the following laps too low and its lap windows drift from the real
car data, so *_tel.json files and laptimes.json columns land on the wrong lap.

Fix: per driver, match FastF1 laps to the official (Jolpica) laps by identical
lap time, rebuild every lap window as race start + cumulative official lap
times (validated against the car's position at the timing line), insert rows
for laps FastF1 never saw, then run the normal extractors on that corrected
session.

Re-running R.py or LapTimes.py for such a race brings the problem back, so
run this afterwards (2020: Austrian Grand Prix).

  python fix_lap_alignment.py . 2020 "Austrian Grand Prix"           # dry run
  python fix_lap_alignment.py . 2020 "Austrian Grand Prix" --apply
"""
import glob
import math
import os
import sys

import numpy as np
import pandas as pd

repo, year, event = os.path.abspath(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
apply = "--apply" in sys.argv
SESSION = "Race"
os.chdir(repo)
sys.path.insert(0, repo)

import fastf1  # noqa: E402

fastf1.Cache.enable_cache("cache")
import LapTimes  # noqa: E402
import R  # noqa: E402
import SessionLapTimes  # noqa: E402

TOL = pd.Timedelta(milliseconds=1)
SHIFT_COLS = ("Time", "LapStartTime", "Sector1SessionTime", "Sector2SessionTime",
              "Sector3SessionTime", "PitOutTime", "PitInTime")
TIMING_COLS = ("Sector1Time", "Sector2Time", "Sector3Time", "Sector1SessionTime",
               "Sector2SessionTime", "Sector3SessionTime", "SpeedI1", "SpeedI2",
               "SpeedFL", "SpeedST", "PitOutTime", "PitInTime")


def align(ff_times, off_times):
    """LCS of two lap-time sequences (equal within 1 ms) -> {official_idx: ff_idx}."""
    n, m = len(off_times), len(ff_times)
    dp = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            a, b = off_times[i], ff_times[j]
            same = pd.notna(a) and pd.notna(b) and abs(a - b) <= TOL
            dp[i, j] = dp[i + 1, j + 1] + 1 if same else max(dp[i + 1, j], dp[i, j + 1])
    i = j = 0
    out = {}
    while i < n and j < m:
        a, b = off_times[i], ff_times[j]
        if pd.notna(a) and pd.notna(b) and abs(a - b) <= TOL:
            out[i] = j; i += 1; j += 1
        elif dp[i + 1, j] >= dp[i, j + 1]:
            i += 1
        else:
            j += 1
    return out


extractor = R.SeasonSessionExtractor(year=year)
# Raw FastF1 laps: R.py's retired-on-track fix must only run after the repair
# (with too few laps it would flag every finisher as stopped on track). Laps
# FastF1 generated past the last official lap are dropped for the same reason;
# the fix re-adds a partial lap for cars that really stopped on track.
session = fastf1.get_session(year, event, SESSION)
session.load(telemetry=True, weather=True, messages=True)
lt_extractor = LapTimes.SeasonSessionExtractor(year=year)

laps = session.laps
fixed_rows, report = [], []
for driver in sorted(laps["Driver"].dropna().unique()):
    ff = laps.pick_drivers(driver).sort_values("LapNumber").reset_index(drop=True)
    ergast = lt_extractor._get_ergast_lap_map(event, session, driver)
    if not ergast:
        report.append((driver, "no official laps; kept as is"))
        fixed_rows.append(pd.DataFrame(ff))
        continue
    off_laps = sorted(ergast)
    off_times = [ergast[n]["LapTime"] for n in off_laps]
    if off_laps != list(range(1, len(off_laps) + 1)) or any(pd.isna(t) for t in off_times):
        report.append((driver, "official laps incomplete; kept as is"))
        fixed_rows.append(pd.DataFrame(ff))
        continue
    match = align(list(ff["LapTime"]), off_times)
    if 0 not in match:
        report.append((driver, "lap 1 not matched; kept as is"))
        fixed_rows.append(pd.DataFrame(ff))
        continue

    t0 = ff.loc[match[0], "LapStartTime"]
    if os.environ.get("ANCHOR") == "end":  # measured end of lap 1 instead of its estimated start
        t0 = ff.loc[match[0], "Time"] - off_times[0]
    ends = t0 + pd.Series(off_times).cumsum()
    starts = pd.concat([pd.Series([t0]), ends[:-1]], ignore_index=True)

    # Validate: at every rebuilt lap end the car should be at the timing line.
    pos = session.pos_data[ff.loc[0, "DriverNumber"]]
    pos = pos[pos["Status"] == "OnTrack"] if "Status" in pos else pos
    st = pos["SessionTime"].to_numpy()
    def xy(t):  # nearest sample; SessionTime is not always monotonic
        k = int(np.abs(st - t.to_timedelta64()).argmin())
        return float(pos["X"].iloc[k]), float(pos["Y"].iloc[k])
    line = xy(ends.iloc[0])
    dev = [math.dist(line, xy(t)) / 10 for t in ends.iloc[:-1]]  # metres

    rows = []
    for i, lap_no in enumerate(off_laps):
        if i in match:
            row = ff.loc[match[i]].copy()
            shift = ends.iloc[i] - row["Time"] if pd.notna(row["Time"]) else pd.Timedelta(0)
            for c in SHIFT_COLS:
                if c in row and pd.notna(row[c]):
                    row[c] = row[c] + shift
            if pd.notna(row.get("LapStartDate")):
                row["LapStartDate"] = row["LapStartDate"] + (starts.iloc[i] - ff.loc[match[i], "LapStartTime"])
        else:
            prev = rows[-1] if rows else ff.loc[match[0]]
            row = prev.copy()
            for c in TIMING_COLS:
                if c in row:
                    row[c] = pd.NaT if "Time" in c else np.nan
            row["TyreLife"] = prev["TyreLife"] + 1 if pd.notna(prev["TyreLife"]) else np.nan
            row["IsPersonalBest"] = False
            row["Position"] = np.nan
            row["TrackStatus"] = np.nan
            row["Deleted"] = np.nan
            row["DeletedReason"] = np.nan
            row["FastF1Generated"] = True
            row["IsAccurate"] = False
            if pd.notna(prev.get("LapStartDate")):
                row["LapStartDate"] = prev["LapStartDate"] + (starts.iloc[i] - prev["LapStartTime"])
        row["LapNumber"] = float(lap_no)
        row["LapTime"] = off_times[i]
        row["LapStartTime"] = starts.iloc[i]
        row["Time"] = ends.iloc[i]
        # FastF1 counts tyre life on its own laps; recount across inserted laps
        if rows and row["Stint"] == rows[-1]["Stint"] and pd.notna(rows[-1]["TyreLife"]):
            row["TyreLife"] = rows[-1]["TyreLife"] + 1
        rows.append(row)
    fixed_rows.append(pd.DataFrame(rows))
    renumbered = sum(1 for i, j in match.items() if ff.loc[j, "LapNumber"] != off_laps[i])
    report.append((driver, f"official {len(off_laps)}, fastf1 {len(ff)}, matched {len(match)}, "
                           f"renumbered {renumbered}, inserted {len(off_laps) - len(match)}, "
                           f"dropped {len(ff) - len(match)}, line deviation max {max(dev, default=0):.1f} m "
                           f"median {np.median(dev) if dev else 0:.1f} m"))

for r in report:
    print(*r)

if not apply:
    sys.exit(0)

fixed = pd.concat(fixed_rows, ignore_index=True)[laps.columns]
for c in laps.columns:
    try:
        fixed[c] = fixed[c].astype(laps[c].dtype)
    except (TypeError, ValueError):
        pass
session._laps = fastf1.core.Laps(fixed, session=session)
session._telemetry_loaded = True
added = R.SeasonSessionExtractor._fix_missing_retired_on_track_laps(session)
print(f"retired-on-track laps added: {added}")
# The fix is not idempotent and get_session() re-applies it on every cache hit.
extractor._fix_missing_retired_on_track_laps = lambda _session: 0
extractor._session_cache[f"{year}-{event}-{SESSION}"] = session

base = f"{event}/{SESSION}"
removed = 0
for f in glob.glob(f"{base}/*/*_tel.json"):
    os.remove(f); removed += 1
print(f"removed {removed} old telemetry files")

key = f"{year}-{event}-{SESSION}"
extractor.process_event_session(event, SESSION)
lt_extractor._session_cache[key] = session
lt_extractor.process_event_session(event, SESSION)
SessionLapTimes.merge_session(event, SESSION)
print("done")
