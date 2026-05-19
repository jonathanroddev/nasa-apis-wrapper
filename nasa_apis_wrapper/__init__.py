"""
Initialization file for the nasa_apis_wrapper module.

This file initializes the package and makes its main classes and services available for import.

Classes:
    APOD: Model representing an Astronomy Picture of the Day object.
    APODRequest: Request model for the APOD endpoint.
    NeoFeed: Model representing a list of near-Earth objects.
    NeoFeedRequest: Request model for the NeoFeed endpoint.
    NearEarthObjectItem: Model for a single near-Earth object.
    NeoBrowse: Model for browsing near-Earth objects.
    Pagination: Model for paginated responses.
    BaseAPI: Base class for interacting with NASA APIs.
    NasaAPIException: Exception class for NASA API errors.
    GenericDonkiRequest: Base request model for DONKI API.
    DonkiCMEResponse: Response model for CME events.
    DonkiCMEAnalysisRequest: Request model for CME analysis.
    CMEAnalysis: Model for CME analysis data.
    DonkiGSTResponse: Response model for GST events.
    DonkiIPSRequest: Request model for IPS events.
    DonkiIPSResponse: Response model for IPS events.
    DonkiFLRResponse: Response model for FLR events.
    DonkiSEPResponse: Response model for SEP events.
    DonkiMPCResponse: Response model for MPC events.
    DonkiRBEResponse: Response model for RBE events.
    DonkiHSSResponse: Response model for HSS events.
    DonkiWSAEnlilSimulationResponse: Response model for WSA-Enlil simulations.
    DonkiNotificationsRequest: Request model for notifications.
    DonkiNotificationResponse: Response model for notifications.
    Utils: Utility functions for the package.

Services:
    APODService: Provides methods to interact with the APOD API.
    NeoWsService: Provides methods to interact with the Near Earth Object Web Service API.
    DonkiService: Provides methods to interact with the DONKI API.

Notes:
    This file is automatically executed when the package is imported and exposes the main interfaces for NASA APIs.
"""

from .apod import APODService, APOD, APODRequest
from .asteroids_neows import (
    NeoFeed,
    NeoFeedRequest,
    NeoWsService,
    NearEarthObjectItem,
    NeoBrowse,
    Pagination,
)
from .base import BaseAPI, NasaAPIException
from .donki import (
    DonkiService,
    GenericDonkiRequest,
    DonkiCMEResponse,
    DonkiCMEAnalysisRequest,
    CMEAnalysis,
    DonkiGSTResponse,
    DonkiIPSRequest,
    DonkiIPSResponse,
    DonkiFLRResponse,
    DonkiSEPResponse,
    DonkiMPCResponse,
    DonkiRBEResponse,
    DonkiHSSResponse,
    DonkiWSAEnlilSimulationResponse,
    DonkiNotificationsRequest,
    DonkiNotificationResponse,
)
from .exoplanet import ExoplanetService, ExoplanetRecord, ExoplanetTable, DiscoveryMethod
from .gibs import GIBSService, GIBSDomains, GIBSProjection, GIBSTileFormat, GIBSWMSFormat, GIBSDataType
from .insight import (
    InsightService,
    InsightWeatherResponse,
    SolData,
    SensorStats,
    WindDirectionData,
    WindPoint,
    SolValidity,
    SensorValidity,
    ValidityChecks,
)
from .epic import (
    EPICService,
    EPICCollection,
    EPICImageFormat,
    EPICImage,
    EPICDateItem,
    Coordinates2D,
    Position3D,
    AttitudeQuaternions,
)
from .eonet import (
    EONETService,
    EONETEvent,
    EONETEventsRequest,
    EONETEventsResponse,
    EONETGeoJSONResponse,
    GeoJSONFeature,
    GeoJSONFeatureProperties,
    GeoJSONGeometry,
    EventCategoryRef,
    EventSourceRef,
    EventGeometry,
    EONETCategory,
    EONETCategoriesResponse,
    EONETCategoryEventsResponse,
    EONETSource,
    EONETSourcesResponse,
    EONETMagnitude,
    EONETMagnitudesResponse,
    EONETLayer,
    EONETLayerCategory,
    EONETLayersResponse,
)

__all__ = [
    "APODService",
    "APOD",
    "APODRequest",
    "NeoFeed",
    "NeoFeedRequest",
    "NeoWsService",
    "NearEarthObjectItem",
    "NeoBrowse",
    "Pagination",
    "BaseAPI",
    "NasaAPIException",
    "DonkiService",
    "GenericDonkiRequest",
    "DonkiCMEResponse",
    "DonkiCMEAnalysisRequest",
    "CMEAnalysis",
    "DonkiGSTResponse",
    "DonkiIPSRequest",
    "DonkiIPSResponse",
    "DonkiFLRResponse",
    "DonkiSEPResponse",
    "DonkiMPCResponse",
    "DonkiRBEResponse",
    "DonkiHSSResponse",
    "DonkiWSAEnlilSimulationResponse",
    "DonkiNotificationsRequest",
    "DonkiNotificationResponse",
    "ExoplanetService",
    "ExoplanetRecord",
    "ExoplanetTable",
    "DiscoveryMethod",
    "GIBSService",
    "GIBSDomains",
    "GIBSProjection",
    "GIBSTileFormat",
    "GIBSWMSFormat",
    "GIBSDataType",
    "InsightService",
    "InsightWeatherResponse",
    "SolData",
    "SensorStats",
    "WindDirectionData",
    "WindPoint",
    "SolValidity",
    "SensorValidity",
    "ValidityChecks",
    "EPICService",
    "EPICCollection",
    "EPICImageFormat",
    "EPICImage",
    "EPICDateItem",
    "Coordinates2D",
    "Position3D",
    "AttitudeQuaternions",
    "EONETService",
    "EONETEvent",
    "EONETEventsRequest",
    "EONETEventsResponse",
    "EONETGeoJSONResponse",
    "GeoJSONFeature",
    "GeoJSONFeatureProperties",
    "GeoJSONGeometry",
    "EventCategoryRef",
    "EventSourceRef",
    "EventGeometry",
    "EONETCategory",
    "EONETCategoriesResponse",
    "EONETCategoryEventsResponse",
    "EONETSource",
    "EONETSourcesResponse",
    "EONETMagnitude",
    "EONETMagnitudesResponse",
    "EONETLayer",
    "EONETLayerCategory",
    "EONETLayersResponse",
]
