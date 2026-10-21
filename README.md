# 2020 Public F1 Telemetry Files — TracingInsights

[![Data](https://img.shields.io/badge/Data-TracingInsights-blue)](https://tracinginsights.com/data)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](/LICENSE)
[![Season](https://img.shields.io/badge/Season-2020-red)](https://github.com/TracingInsights/2020)

> Free, public Formula 1 telemetry data for the 2020 season. Analyze, visualize, and build with raw session data from every Grand Prix weekend.
>
> **[View on GitHub](https://github.com/TracingInsights/2020)** · **[Analyze/Visualize at f1tel.com](https://f1tel.com)** · **[TracingInsights.com](https://tracinginsights.com)** · **[Ask AI](https://tracinginsights.com)**

---

## 📚 Data Reference

For a detailed explanation of every field and JSON structure in this repository, see **[DATA_REFERENCE.md](DATA_REFERENCE.md)**.

It covers all telemetry, timing, weather, race control, driver, team radio, and circuit/corner data formats used in this repo.

---

## 🗂️ Data For Other Seasons

[2026](https://github.com/TracingInsights/2026) | [2025](https://github.com/TracingInsights/2025) | [2024](https://github.com/TracingInsights/2024) | [2023](https://github.com/TracingInsights/2023) | [2022](https://github.com/TracingInsights/2022) | [2021](https://github.com/TracingInsights/2021) | [2019](https://github.com/TracingInsights/2019) | [2018](https://github.com/TracingInsights/2018) | [Historical Data](https://github.com/TracingInsights/Historical) | [Pitstops](https://github.com/TracingInsights/Pitstops) | [Download Data in CSV](https://github.com/TracingInsights/CSV) | [Data Page](https://tracinginsights.com/data)

---

## 📁 Repository Structure

Each Grand Prix weekend is organized by event and session. Inside each session folder you will find JSON files for drivers, race control messages, circuit corners, lap times, weather, and team radio.

```text
2020/
├── Bahrain Grand Prix/
│   ├── Practice 1/
│   ├── Practice 2/
│   ├── Practice 3/
│   ├── Qualifying/
│   └── Race/
│       ├── drivers.json
│       ├── rcm.json
│       ├── corners.json
│       ├── session_laptimes.json
│       ├── team_radio.json
│       ├── weather.json
│       └── <driver>/
│           ├── laptimes.json
│           ├── <lap>_tel.json
│           └── radio/
│               └── <clip>.mp3
├── ... (17 Grands Prix)
├── images/
│   ├── drivers/
│   │   ├── Mercedes/
│   │   │   ├── BOT.png
│   │   │   ├── HAM.png
│   │   │   └── RUS.png
│   │   ├── Williams/
│   │   │   ├── AIT.png
│   │   │   ├── LAT.png
│   │   │   └── RUS.png
│   │   └── ...
│   ├── headshots/
│   │   └── <team>/<driver>.png
│   ├── cars/
│   │   └── <team>.png
│   └── manifest.json
└── sections/
    └── <circuit>.json
```

Most events have **Practice 1/2/3**, **Qualifying**, and **Race**. 2020 had no sprint weekends, and pre-season testing is not included.

The 17 events of the revised 2020 calendar: Austrian, Styrian, Hungarian, British, 70th Anniversary, Spanish, Belgian, Italian, Tuscan, Russian, Eifel, Portuguese, Emilia Romagna, Turkish, Bahrain, Sakhir, and Abu Dhabi Grand Prix.

> **Note:** Not every weekend ran three practice sessions:
> - **Styrian Grand Prix Practice 3** was cancelled because of rain, so `Styrian Grand Prix/Practice 3/` only contains an empty `drivers.json`, `rcm.json` and `weather.json`.
> - **Eifel Grand Prix** Practice 1 and 2 were cancelled because of bad weather, so the event only has `Practice 3`, `Qualifying` and `Race`.
> - **Emilia Romagna Grand Prix** used a two-day format with a single practice session, so the event only has `Practice 1`, `Qualifying` and `Race`.

> **Note:** F1's live timing archive only has car and position data for Hungarian Grand Prix Practice 1 from about 30 minutes into the session, so roughly 230 of its 582 laps have lap times but no `*_tel.json` file.

> **Note:** In the Austrian Grand Prix Race, F1's timing feed dropped about five laps (official laps 9-13 for most drivers), so FastF1 numbered every later lap too low. The race was re-extracted with each lap window rebuilt from the official (Jolpica) lap times, so `laptimes.json` and `*_tel.json` use the official lap numbers. The laps the feed missed have lap time, position and telemetry, but no sector times or speed traps, and `ff1G` is `true`. Alexander Albon's position data (`x`, `y`, `z`) is frozen from about lap 19 onwards in F1's archive; his other telemetry channels are complete.

---

## 🖼️ Driver & Car Images

Official Formula 1 images are saved under `images/`, keyed by the `team` and `driver` fields of `drivers.json` so a path can be built straight from any entry:

| Folder | Contents | Source |
|---|---|---|
| `images/drivers/<team>/<driver>.png` | 1920 × 1920 driver portrait in the 2020 race suit | 2020 driver pages of formula1.com |
| `images/headshots/<team>/<driver>.png` | 840 × 840 headshot, the source asset behind the thumbnail linked by the `url` field in `drivers.json` | `media.formula1.com` |
| `images/cars/<team>.png` | 465 × 138 side view of the 2020 car | 2020 team pages of formula1.com |

Every file is the untransformed asset served by `media.formula1.com`, with no resizing or re-encoding. The 2026 repository uses WebP cutouts from the current formula1.com CDN, but that CDN has no 2020 assets, so this season uses the 2020 site's own PNG images.

Driver images are keyed by driver **and** team because some drivers drove for another team: George Russell raced for Mercedes at the Sakhir Grand Prix while Lewis Hamilton was out, so there is both a `Williams/RUS.png` and a `Mercedes/RUS.png`. The 2020 site had one portrait per driver, so both of a driver's pairings get the same portrait.

Stand-in and practice-only drivers have some gaps:

- Mick Schumacher (Haas, Abu Dhabi FP1) has no 2020 portrait, so his 2021 Haas portrait is used.
- Robert Kubica (Alfa Romeo Racing, FP1 only) and Roy Nissany (Williams, FP1 only) have no portrait on the host; Nissany has no headshot either.
- `drivers.json` has no headshot `url` for Jack Aitken, Pietro Fittipaldi, Nico Hülkenberg (Racing Point), Robert Kubica and Mick Schumacher; their headshots are taken from F1's legacy driver assets instead.

In total there are 25 driver portraits, 26 headshots and 10 cars. `images/manifest.json` lists every saved file with the driver's name, pixel size and source URL.

Fetch one directly:

```bash
curl -L -o RUS.png "https://raw.githubusercontent.com/TracingInsights/2020/main/images/drivers/Mercedes/RUS.png"
```

To refresh, run `python3 download_images.py` (add `--force` to re-download everything, or `--only cars` for a single set).

---

## 🎙️ Team Radio

Team radio clips F1 published in its live timing archive are saved as MP3 files in each driver's folder, with an index per session:

| Path | Contents |
|---|---|
| `<event>/<session>/<driver>/radio/<file>.mp3` | Original team radio recording from the F1 live timing archive, e.g. `Bahrain Grand Prix/Race/HAM/radio/LEWHAM01_44_20201129_153950.mp3` |
| `<event>/<session>/team_radio.json` | Every clip of the session sorted by time: driver, driver number, UTC date, local file path, and source URL |

[OpenF1](https://openf1.org), the source used in the 2026 repository, has no data before 2023, so `team_radio.py` reads each session's `TeamRadio.json` from the live timing archive directly (this needs [F1 TV authentication](#-f1-tv-authentication)). The `team_radio.json` columns are the same as in the 2026 repository. Only the clips F1 broadcasts are available: 5,624 clips over 80 sessions, between 11 and 192 per session.

Run `python3 team_radio.py` to download every session (or `--events "Monaco Grand Prix"` for one event); existing files are skipped.

---

## 🔐 F1 TV Authentication

Since 15 October 2026, `livetiming.formula1.com` only serves its archive to F1 TV subscribers ([FastF1 issue #978](https://github.com/theOehrly/Fast-F1/issues/978)). This only matters if you want to **regenerate** the data; reading the files in this repository needs no account.

The scripts need **FastF1 3.9.0a0 or newer** (`fastf1>=3.9.0a0` in `requirements.txt`), which adds the F1 TV token to every live timing request itself.

**Locally**, sign in once:

```bash
pip install -r requirements.txt
python -m fastf1 auth f1tv --authenticate   # stores the token
python -m fastf1 auth f1tv --status          # check it
```

FastF1 stores the token at `~/.local/share/fastf1/f1auth_token.json` on Linux (the `platformdirs` user data directory for `fastf1` on other systems). Never commit this file.

**In GitHub Actions**, the composite action `.github/actions/f1-auth` gives FastF1 its credentials from repository secrets:

| Secret | Contents |
|---|---|
| `F1_USERNAME`, `F1_PASSWORD` | F1 account login; FastF1 signs in non-interactively (`FASTF1_AUTH_METHOD=password`) whenever it has no valid token |
| `F1AUTH_TOKEN` | Contents of a `f1auth_token.json` from a machine that signed in; expires after a few days |

Set either one (or both). The session workflows also route their traffic through a Tailscale exit node, which needs the `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET` and `TS_EXIT_NODE` secrets.

---

## 🛠️ Scripts & Workflows

| Script | Workflow | What it does |
|---|---|---|
| `FP1.py`, `FP2.py`, `FP3.py`, `Q.py`, `R.py` | `FP1`, `FP2`, `FP3`, `Q`, `R` | Full extraction for one session type: per-lap telemetry, `laptimes.json`, `drivers.json`, `weather.json`, `rcm.json`, `corners.json`, `session_laptimes.json` |
| `LapTimes.py` | `LappyTimey` | Lap times only; Race lap times and positions from Ergast/Jolpica |
| `SessionLapTimes.py` | `SessionLappyTimey` | Merges every driver's `laptimes.json` into `session_laptimes.json` |
| `corner.py` | `cor` | Rewrites `corners.json` for every session without re-extracting telemetry (`--events`, `--sessions` to limit) |
| `team_radio.py` | `team_radio` | Downloads team radio MP3s and writes `team_radio.json` |
| `fix_lap_alignment.py` | — | Rebuilds lap numbering for a race where F1's timing feed dropped laps (Austrian Grand Prix Race); run after re-extracting that race |
| `download_images.py` | — | Driver, headshot and car images under `images/` |
| `sync_hf_bucket.py` | `sync_hf_bucket` | Uploads the repository to the Hugging Face bucket (see below) |
| — | `release` | Creates a GitHub release for every new commit on `main` (see [CDN](#fetch-via-cdn-jsdelivr)) |

All data workflows are started manually (`workflow_dispatch`), since the 2020 season is complete; `release` runs on its own after each of them (and on direct pushes to `main`). The older analysis scripts (`average_race_pace.py`, `fastest_lap.py`, `lap_position.py`, `overtakes.py`, `strategy.py`, `top_speeds.py`, `bot.ipynb`) are kept as they were.

The per-session extraction scripts process the events left uncommented in their `TARGET_EVENT_NAMES_LIST`.

---

## ⚡ Quick Start

Clone this repository:

```bash
git clone https://github.com/TracingInsights/2020.git
cd 2020
```

Read a JSON file directly in Python:

```python
import json
from pathlib import Path

# Load race lap times for the Bahrain Grand Prix
laptimes = json.loads(
    Path("Bahrain Grand Prix/Race/session_laptimes.json").read_text()
)

# Load weather data for Practice 1
weather = json.loads(
    Path("Bahrain Grand Prix/Practice 1/weather.json").read_text()
)
```

Or fetch a file via GitHub's raw URL:

```bash
curl -L https://raw.githubusercontent.com/TracingInsights/2020/main/Bahrain%20Grand%20Prix/Race/session_laptimes.json
```

### Fetch via CDN (jsDelivr)

Every push to this repository creates a GitHub release with a semver tag of the form `<year>.<day-of-year>.<build>`, where the year is when the release was made, not the season (e.g. `2026.292.1`). You can fetch any file through jsDelivr pinned to that release:

```text
https://cdn.jsdelivr.net/gh/TracingInsights/2020@2026.292.1/Bahrain%20Grand%20Prix/Race/session_laptimes.json
```

To get the latest data, resolve the current release tag first (both requests are fast and CORS-enabled):

```javascript
const release = await fetch(
  "https://api.github.com/repos/TracingInsights/2020/releases/latest"
).then(r => r.json());

const url = `https://cdn.jsdelivr.net/gh/TracingInsights/2020@${release.tag_name}/Bahrain%20Grand%20Prix/Race/session_laptimes.json`;
```

```bash
TAG=$(curl -s https://api.github.com/repos/TracingInsights/2020/releases/latest | jq -r .tag_name)
curl -L "https://cdn.jsdelivr.net/gh/TracingInsights/2020@${TAG}/Bahrain%20Grand%20Prix/Race/session_laptimes.json"
```

You can also use a branch directly (cached for 12 hours) if you don't need release pinning:

```text
https://cdn.jsdelivr.net/gh/TracingInsights/2020@main/Bahrain%20Grand%20Prix/Race/session_laptimes.json
```

> **Note:** jsDelivr serves individual files up to 20 MB. The latest release tag is also available from jsDelivr's own API:
> `https://data.jsdelivr.com/v1/packages/gh/TracingInsights/2020/resolved?specifier=latest`

### Hugging Face bucket

The same files are mirrored to the Hugging Face bucket `hf://buckets/tracinginsights/2020`. The `sync_hf_bucket` workflow (manual, needs an `HF_TOKEN` secret) uploads new and changed files; locally:

```bash
export HF_TOKEN=hf_...            # write token; never commit it
uv run sync_hf_bucket.py --dry-run
uv run sync_hf_bucket.py
```

---

## ❓ Frequently Asked Questions

### What kind of data is available?

Our repositories contain various types of Formula 1 data including:

- Detailed telemetry data (speed, throttle, brake, DRS)
- Acceleration data (lateral, longitudinal, vertical)
- Technical data (RPM, gear, elevation)
- Race results and qualifying times
- Lap times and pit stop information
- Team radio clips
- Driver and constructor standings

The data is organized by season and follows a consistent format for easy access and analysis.

### When is data updated?

The 2020 season is complete, so this repository is only updated when the extraction scripts or data formats change. For current seasons, we typically update the data **30 minutes after each session** of a Grand Prix weekend.

You can analyze comprehensive telemetry data including:

- Speed (km/h)
- Throttle input percentage
- Brake application
- Gear selection
- DRS activation zones
- Lateral acceleration (G-forces)
- Longitudinal acceleration
- Track elevation changes
- Engine RPM
- Vertical acceleration

### Fuel Correction

Fuel Correction adjusts lap times to account for the changing weight of fuel in Formula 1 cars during a race. As cars burn fuel, they become progressively lighter, resulting in naturally faster lap times even without any improvement in driving or track conditions.

**Why Fuel Correction matters:**

- **Weight impact:** Each kilogram of fuel adds approximately 0.03 seconds per lap to a car's time
- **Race strategy analysis:** Helps distinguish between genuine pace improvements and those simply due to fuel load reduction
- **Fair comparison:** Enables meaningful comparison between laps from different stages of a race
- **Performance evaluation:** Provides a clearer picture of true car and driver performance throughout a race

**How Fuel Correction is calculated:**

```
Corrected Lap Time = Original Lap Time - (Fuel Weight Effect)
```

Where:

```
Fuel Weight Effect = Remaining Fuel (kg) × 0.03 seconds
Remaining Fuel = Initial Fuel × (1 - Current Lap / Total Race Laps)
```

The calculation uses these standard assumptions:

- **Initial fuel load:** 100kg
- **Fuel consumption:** Linear usage throughout the race (equal amount burned each lap)
- **Performance impact:** 0.03 seconds per kilogram of fuel per lap (industry standard approximation)

**How to interpret Fuel-Corrected lap times:**

- **Early race laps:** Will show faster corrected times than their actual times (compensating for heavy fuel load)
- **Mid-race laps:** Will show moderate correction
- **Late race laps:** Will show minimal correction (as cars are already light on fuel)
- **Comparing drivers:** Reveals true pace differences independent of fuel load advantages
- **Stint analysis:** Helps identify genuine tire degradation separate from the fuel weight effect

**When to use Fuel Correction:**

- **Race pace analysis:** When comparing laps from different stages of a race
- **Strategy evaluation:** When analyzing the effectiveness of different pit stop strategies
- **Driver performance:** When assessing a driver's consistency throughout a race
- **Team comparisons:** When comparing the race pace of different teams

> **Note:** Fuel correction is an approximation based on standard assumptions. Actual fuel loads and consumption rates may vary between teams, cars, and race conditions. The correction provides a useful analytical tool but should be considered alongside other performance metrics.

### Elevation Chart

The Elevation Chart is a critical tool for verifying data integrity and alignment between different drivers' telemetry. Since track elevation is a fixed geographical feature, all drivers should show nearly identical elevation profiles regardless of their performance.

**Why the Elevation Chart matters for data integrity:**

- **Reference alignment:** Track elevation is a constant physical property that all cars experience identically
- **Data synchronization check:** Misaligned elevation profiles immediately indicate synchronization issues
- **Error detection:** Helps identify corrupted or incorrectly processed telemetry data
- **Baseline verification:** Establishes confidence in the reliability of other telemetry channels

**How to use the Elevation Chart for data validation:**

- **Visual inspection:** Compare elevation profiles between multiple drivers - they should closely overlap
- **Pattern matching:** Look for consistent peaks and valleys across all selected drivers
- **Offset detection:** Check for horizontal shifts that indicate distance measurement errors
- **Anomaly identification:** Identify unusual spikes or drops that may indicate sensor errors

**Common data integrity issues revealed by the Elevation Chart:**

- **Horizontal misalignment:** Indicates distance measurement or synchronization errors
- **Vertical scaling differences:** May indicate drivers going over kerbs/bumps
- **Missing segments:** Reveals data gaps or transmission failures during recording
- **Noise or jitter:** Can indicate sensor interference or data processing problems
- **Complete mismatch:** Suggests incorrect lap selection or major data corruption

> **Pro tip:** Always check the Elevation Chart first before analyzing other telemetry channels. If elevation profiles don't align properly, it's a strong indication that other telemetry comparisons (speed, throttle, braking) may be unreliable for that particular dataset.

> **Note:** Minor variations in elevation data between drivers are normal due to sensor precision and sampling rates. However, significant differences that alter the overall profile shape indicate data integrity issues.

### Data Archives Overview

TracingInsights provides comprehensive Formula 1 data archives from 1950 to the present day, organized by season. Our data is collected from various sources including the Ergast/Jolpica API and F1 official feeds via FastF1.

**Types of data available in our archives:**

- **Telemetry data:** Detailed car performance metrics including speed, throttle, brake, DRS usage, and acceleration
- **Race results:** Complete race classifications, finishing positions, and points for all seasons
- **Lap times:** Detailed timing information for every lap by each driver
- **Pit stops:** Timing and duration of all pit stops during races
- **Weather data:** Track and ambient conditions for different circuits and races
- **Penalty points:** Current penalty point standings for each driver
- **Historical statistics:** Complete race results database from 1950 onwards with driver and constructor standings

**Disclaimer:** This data is provided for free. TracingInsights is not affiliated with Formula 1, FIA, or any F1 team. All trademarks belong to their respective owners.

[Visit Data Archives Page](https://tracinginsights.com/data)

### Can I use this data for my personal projects?

Yes, you can use this data as you wish. We encourage creative use of the data for:

- Data analysis and research
- Visualization projects
- Academic work
- Personal applications

If you publish or share your work, attribution to TracingInsights is appreciated but not required.

### I found an error in the data. How can I report it?

If you find any errors or inconsistencies in our data, you can:

- Open an issue on the relevant GitHub repository
- Contact us through our [contact page](https://tracinginsights.com/contact/)

We appreciate community contributions to improve data accuracy.

### Do I need an API key to access the data?

No, you don't need an API key. All our data is freely available through the GitHub repositories. Simply:

1. Clone or download the repository you're interested in
2. Access the files directly from your local machine
3. Or use GitHub's raw file URLs in your applications

This approach ensures the data remains accessible to everyone without authentication barriers. (Only regenerating the data from F1's live timing archive needs an F1 TV account; see [F1 TV Authentication](#-f1-tv-authentication).)

Have a question that's not answered here? Check the README files in each repository for specific details about that season's data, or [contact us](https://tracinginsights.com/contact/) for additional help.

---

## 👥 Authors

- [@TracingInsights](https://github.com/TracingInsights)

---

## 🤝 Support the project

- [Report issues or Feature Requests](https://github.com/TracingInsights/2020/issues)
- [Sponsor](https://github.com/sponsors/TracingInsights)
- [Star the project on GitHub](https://github.com/TracingInsights/2020)

---

## 💬 Feedback

If you have any feedback, please reach out to us at https://tracinginsights.com/contact/

---

## 🙏 Credits

- [FastF1](https://github.com/theOehrly/Fast-F1)
- [MultiViewer](https://github.com/f1multiviewer)
- [Ergast/Jolpica](https://github.com/jolpica/jolpica-f1)
- [OpenF1](https://openf1.org)

---

## 📄 License

Apache-2.0 license

---

## ⚠️ Notice

TracingInsights and this website are unofficial and are not associated in any way with
the Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD
CHAMPIONSHIP, GRAND PRIX and related marks are trade marks of Formula One
Licensing B.V.
