## Official documentation

[NASA APIs](https://api.nasa.gov/)

## Examples of usage

```python
import datetime
from typing import List, Dict

from devtools import pprint

from nasa_apis_wrapper import (
    APODService,
    APOD,
    APODRequest,
    NeoWsService,
    NeoFeed,
    NasaAPIException,
    NearEarthObjectItem,
    NeoBrowse,
    Pagination,
)

api_key = "<YOUR_API_KEY>"

apod_service: APODService = APODService(api_key)

try:
    # APOD
    apod: APOD = apod_service.get_astronomy_picture_of_day(APODRequest(date=datetime.date(2022, 3, 27)))
    pprint(apod)

    # Asteroids NeoWs
    neows_service: NeoWsService = NeoWsService(api_key)
    neo_feed: NeoFeed = neows_service.feed()
    # neo_feed: NeoFeed = neows_service.feed(NeoFeedRequest(start_date=datetime.date(202, 1, 1)))
    pprint(neo_feed)

    if neo_feed:
        keys = neo_feed.near_earth_objects.model_dump().keys()
        near_earth_objects_date_list_dict: List[Dict] = neo_feed.near_earth_objects.model_dump().get(next(iter(keys)))
        neo_item_list: List[NearEarthObjectItem] = []
        for item in near_earth_objects_date_list_dict:
            neo_item_list.append(NearEarthObjectItem(**item))
        neo_lookup: NearEarthObjectItem = neows_service.lookup(neo_item_list[0].id)
        pprint(neo_lookup)

    pagination: Pagination = Pagination(page=1, size=10)
    neo_browse: NeoBrowse = neows_service.browse(pagination)
    pprint(neo_browse)
except NasaAPIException as e:
    print(e)
```

## Helpful commands

```console
 poetry run pytest
 poetry run pytest --cov
 poetry run pytest --cov --cov-report term-missing
```
