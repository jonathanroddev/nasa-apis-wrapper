from typing import Optional

from pydantic import BaseModel, ConfigDict


class EarthAssetResource(BaseModel):
    """Dataset and planet metadata embedded in an Earth asset record."""
    model_config = ConfigDict(extra="ignore")

    dataset: Optional[str] = None
    planet: Optional[str] = None


class EarthAsset(BaseModel):
    """
    Metadata for an available Landsat 8 image at a given location and date,
    returned by ``GET /planetary/earth/assets``.

    ``url`` is a direct link to the GeoTIFF image on Google Cloud Storage.
    ``cloud_score`` (0.0–1.0) is only present when the imagery endpoint was
    called with ``cloud_score=True``; it estimates the fraction of the image
    covered by clouds.
    """
    model_config = ConfigDict(extra="ignore")

    date: Optional[str] = None              # ISO 8601 datetime of the image
    url: Optional[str] = None               # GeoTIFF URL on GCS
    cloud_score: Optional[float] = None     # 0.0–1.0, omitted unless requested
    resource: Optional[EarthAssetResource] = None
    service_version: Optional[str] = None
