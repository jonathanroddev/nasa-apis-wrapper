# nasa-apis-wrapper

[![PyPI version](https://img.shields.io/pypi/v/nasa-apis-wrapper)](https://pypi.org/project/nasa-apis-wrapper/)
[![Python](https://img.shields.io/pypi/pyversions/nasa-apis-wrapper)](https://pypi.org/project/nasa-apis-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Disclaimer:** This is an unofficial, community-maintained Python wrapper. It is not affiliated with, endorsed by, or in any way connected to NASA.

A typed Python wrapper for [NASA's public APIs](https://api.nasa.gov/), built on **Pydantic v2** and **requests**. Every response is a validated model with IDE autocompletion — no raw dicts.

## Installation

```bash
pip install nasa-apis-wrapper
```

Requires Python 3.12+.

## API Key

Most NASA APIs accept a free API key from [api.nasa.gov](https://api.nasa.gov/). Without one you can use the demo key `DEMO_KEY`, which has stricter rate limits (30 requests/hour, 50/day).

Pass the key when constructing any service that requires it:

```python
from nasa_apis_wrapper import APODService

apod = APODService(api_key="YOUR_KEY_HERE")
```

Services that don't require a key (EONET, EPIC, Exoplanet, GIBS, Image Library, CNEOS, SSC, OSDR, Trek) are instantiated without arguments.

## API Coverage

| Service | Class | API Key | Status |
|---------|-------|---------|--------|
| Astronomy Picture of the Day | `APODService` | Required | ✓ |
| Asteroids — NeoWs | `NeoWsService` | Required | ✓ |
| DONKI (space weather) | `DonkiService` | Required | ✓ |
| Earth imagery | `EarthService` | Required | ✗ Backend down |
| EONET (natural events) | `EONETService` | No | ✓ |
| EPIC (Earth polychromatic imaging) | `EPICService` | No | ✓ |
| Exoplanet Archive | `ExoplanetService` | No | ✓ |
| GIBS (satellite imagery tiles) | `GIBSService` | No | ✓ |
| NASA Image & Video Library | `ImageLibraryService` | No | ✓ |
| InSight Mars weather | `InsightService` | Required | ✓ (data frozen Dec 2022) |
| Mars Rover Photos | `MarsRoverService` | Required | ✗ Backend down |
| OSDR (space biology data) | `OSDRService` + `RadLabService` + `BioDataService` | No | ✓ |
| SSD/CNEOS (small bodies) | `CNEOSService` | No | ✓ |
| Satellite Situation Center | `SSCService` | No | ✓ |
| TechPort (NASA projects) | `TechportService` | No | ✗ 403 Forbidden |
| TechTransfer | `TechTransferService` | Required | ✗ 404 Endpoint removed |
| TLE (orbital elements) | `TLEService` | No | ✗ Service down |
| Vesta/Moon/Mars Trek WMTS | `TrekService` | No | ✓ (tile endpoints only) |

## Usage

### APOD — Astronomy Picture of the Day

```python
from nasa_apis_wrapper import APODService, APODRequest

apod = APODService(api_key="YOUR_KEY")

# Today's picture
pic = apod.get_astronomy_picture_of_day()
print(pic.title, pic.url)

# Specific date
pic = apod.get_astronomy_picture_of_day(APODRequest(date="2024-01-01"))

# Random batch
pics = apod.get_astronomy_pictures(APODRequest(count=5))

# Date range
pics = apod.get_astronomy_pictures(APODRequest(start_date="2024-01-01", end_date="2024-01-07"))
```

### NeoWs — Near Earth Objects

```python
from nasa_apis_wrapper import NeoWsService, NeoFeedRequest

neows = NeoWsService(api_key="YOUR_KEY")

feed = neows.feed(NeoFeedRequest(start_date="2024-01-01", end_date="2024-01-07"))
print(feed.element_count, "NEOs this week")

neo = neows.lookup(2000433)  # 433 Eros by SPK-ID
print(neo.name, neo.is_potentially_hazardous_asteroid)

page = neows.browse()  # paginated full catalogue
```

### DONKI — Space Weather

```python
from nasa_apis_wrapper import DonkiService, GenericDonkiRequest, DonkiIPSRequest

donki = DonkiService(api_key="YOUR_KEY")
req = GenericDonkiRequest(startDate="2024-01-01", endDate="2024-01-31")

cmes        = donki.cme(req)               # Coronal Mass Ejections
flares      = donki.flr(req)               # Solar Flares
storms      = donki.gst(req)               # Geomagnetic Storms
particles   = donki.sep(req)               # Solar Energetic Particles
streams     = donki.hss(req)               # High Speed Streams
shocks      = donki.ips(DonkiIPSRequest(startDate="2024-01-01", endDate="2024-01-31"))
simulations = donki.wsa_enlil_simulation(req)
```

### EONET — Natural Events

```python
from nasa_apis_wrapper import EONETService, EONETEventsRequest

eonet = EONETService()

events = eonet.events(EONETEventsRequest(category="wildfires", days=30))
for e in events.events:
    print(e.id, e.title)

categories = eonet.categories()
layers = eonet.layers("wildfires")
```

### EPIC — Earth Polychromatic Imaging Camera

```python
from nasa_apis_wrapper import EPICService

epic = EPICService()

images = epic.images()                          # latest natural colour
images = epic.images("enhanced")               # latest enhanced
images = epic.images("natural", date="2024-01-15")

for img in images:
    url = epic.image_url(img, "natural", "png")
    print(img.date, url)

dates = epic.available_dates()
```

### Exoplanet Archive

```python
from nasa_apis_wrapper import ExoplanetService

exo = ExoplanetService()

planets = exo.confirmed_planets(limit=10)
transits = exo.planets_by_method("Transit", limit=5)
trappist = exo.planet("TRAPPIST-1 b")
print(trappist.pl_name, trappist.hostname, trappist.pl_orbper)

# Raw ADQL query
rows = exo.query("SELECT TOP 5 pl_name, hostname, disc_year FROM pscomppars")
```

### GIBS — Global Imagery Browse Services

Serves NASA satellite imagery tiles (WMTS/WMS).

```python
from nasa_apis_wrapper import GIBSService

gibs = GIBSService()

# Build tile/WMS URLs
url = gibs.tile_url("MODIS_Terra_CorrectedReflectance_TrueColor", "250m", 3, 2, 5, date="2024-01-15")
wms = gibs.wms_url("MODIS_Terra_CorrectedReflectance_TrueColor", "-180,-90,180,90", 512, 256, date="2024-01-15")

# Download tile bytes
tile_bytes = gibs.get_tile("MODIS_Terra_CorrectedReflectance_TrueColor", "250m", 0, 0, 0, date="2024-01-15")

domains = gibs.describe_domains("MODIS_Terra_CorrectedReflectance_TrueColor", "250m")
print(domains.start_date, domains.end_date)
```

### NASA Image & Video Library

```python
from nasa_apis_wrapper import ImageLibraryService, ImageLibrarySearchRequest

lib = ImageLibraryService()

results = lib.search(ImageLibrarySearchRequest(q="Apollo 11", media_type="image", page_size=10))
print(results.collection.metadata.total_hits, "results")

for item in results.collection.items:
    print(item.metadata.nasa_id, item.metadata.title)
    print(item.thumbnail)  # preview URL

asset = lib.asset("as11-40-5931")
print(asset.urls)  # all rendition URLs

album = lib.album("Apollo-at-50")
```

### SSD/CNEOS — Small Body Database

```python
from nasa_apis_wrapper import CNEOSService, FireballRequest, CADRequest

cneos = CNEOSService()

fireballs = cneos.fireballs(FireballRequest(date_min="2024-01-01"))
for fb in fireballs.records:
    print(fb.date, fb.energy)

cad = cneos.close_approaches(CADRequest(date_min="2024-01-01", dist_max="0.05"))
for c in cad.records:
    print(c.des, c.cd, c.dist)

body = cneos.object(sstr="ceres")      # by name
body = cneos.object(des="433")         # by designation

sentry = cneos.sentry_summary()        # impact risk objects
nhats  = cneos.nhats_summary()         # human-accessible NEOs

cal = cneos.jd_to_date(2451545.0)
print(cal.cd)                          # "2000-01-01 12:00:00"
```

### SSC — Satellite Situation Center

```python
from nasa_apis_wrapper import SSCService

ssc = SSCService()

observatories = ssc.observatories()
iss = ssc.observatories(id="iss")[0]
print(iss.Id, iss.Name)

stations = ssc.ground_stations()
```

### OSDR — Open Science Data Repository

Three sub-services under the OSDR umbrella:

```python
from nasa_apis_wrapper import OSDRService, OSDRSearchRequest, RadLabService, RadLabRequest, BioDataService

# Search space biology studies
osdr = OSDRService()
results = osdr.search(OSDRSearchRequest(term="microgravity"))
print(results.hits.total, "studies")

for hit in results.hits.hits:
    print(hit.source.accession, hit.source.study_title)

files = osdr.study_files("OSD-48")

# Radiation measurements
radlab = RadLabService()
measurements = radlab.measurements(RadLabRequest(instrument="TEPC"))
for m in measurements:
    print(m.timestamp, m.instrument_id)

# Biological data
bio = BioDataService()
datasets = bio.datasets()          # {accession: url}
assays = bio.assays("OSD-48")
samples = bio.samples("OSD-48", assays[0])
```

### Trek WMTS — Vesta / Moon / Mars

```python
from nasa_apis_wrapper import TrekService

trek = TrekService()

# Build tile/WMS URLs (body = "mars", "moon", or "vesta")
tile_url = trek.tile_url("mars", "Mars_Viking_MDIM21_ClrMosaic_global_232m", 0, 0, 0)
wms_url  = trek.wms_url("moon", "LRO_WAC_Mosaic_Global_303m", "-180,-90,180,90", 512, 256)

# Download tile bytes
tile = trek.get_tile("mars", "Mars_Viking_MDIM21_ClrMosaic_global_232m", 0, 0, 0)
```

### InSight — Mars Weather

Data from the InSight lander. The mission ended in December 2022 — the last 7 sols (675–681) are always returned.

```python
from nasa_apis_wrapper import InsightService

insight = InsightService(api_key="YOUR_KEY")
weather = insight.weather()
for sol in weather.sol_keys:
    data = getattr(weather, sol)
    print(f"Sol {sol}: {data}")
```

## Error Handling

All network errors, HTTP errors, and malformed responses raise `NasaAPIException`:

```python
from nasa_apis_wrapper import APODService, NasaAPIException

try:
    apod = APODService(api_key="INVALID_KEY")
    pic = apod.get_astronomy_picture_of_day()
except NasaAPIException as e:
    print(e)
```

## Development

```bash
uv run pytest
uv run pytest --cov --cov-report term-missing
uv run black nasa_apis_wrapper tests
```

## License

MIT — see [LICENSE](LICENSE).

## Official documentation

[https://api.nasa.gov/](https://api.nasa.gov/)
