from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


ExoplanetTable = Literal[
    "pscomppars",
    "ps",
    "toi",
    "stellarhosts",
    "ml",
    "k2pandc",
    "spectra",
]

DiscoveryMethod = Literal[
    "Transit",
    "Radial Velocity",
    "Imaging",
    "Microlensing",
    "Astrometry",
    "Eclipse Timing Variations",
    "Transit Timing Variations",
    "Pulsation Timing Variations",
    "Orbital Brightness Modulation",
    "Disk Kinematics",
]


class ExoplanetRecord(BaseModel):
    """
    A planet record from the NASA Exoplanet Archive.

    Models the most commonly used columns from ``pscomppars`` and ``ps``.
    Additional columns returned by the API (e.g. uncertainty fields, photometric
    magnitudes, reflinks) are silently ignored — use :meth:`ExoplanetService.query`
    for full column access.

    Units:
        - Mass: Earth masses (``pl_masse``) / Jupiter masses (``pl_massj``)
        - Radius: Earth radii (``pl_rade``) / Jupiter radii (``pl_radj``)
        - Orbital period: days
        - Semi-major axis: au
        - Stellar mass: Solar masses
        - Distance: parsecs
        - Temperature: Kelvin
    """

    model_config = ConfigDict(extra="ignore")

    # Identification — never null
    pl_name: str
    hostname: str

    # Identification — optional
    pl_letter: Optional[str] = None
    hd_name: Optional[str] = None
    hip_name: Optional[str] = None
    tic_id: Optional[str] = None

    # Discovery
    disc_year: Optional[int] = None
    discoverymethod: Optional[str] = None
    disc_facility: Optional[str] = None
    disc_telescope: Optional[str] = None

    # ps table specific (not present in pscomppars)
    default_flag: Optional[int] = None
    soltype: Optional[str] = None

    # Planetary orbital parameters
    pl_orbper: Optional[float] = None     # orbital period (days)
    pl_orbsmax: Optional[float] = None    # semi-major axis (au)
    pl_orbeccen: Optional[float] = None   # eccentricity
    pl_orbincl: Optional[float] = None    # inclination (deg)

    # Planetary physical parameters
    pl_rade: Optional[float] = None       # radius (Earth radii)
    pl_radj: Optional[float] = None       # radius (Jupiter radii)
    pl_masse: Optional[float] = None      # mass (Earth masses)
    pl_massj: Optional[float] = None      # mass (Jupiter masses)
    pl_bmasse: Optional[float] = None     # best mass estimate (Earth masses)
    pl_bmassj: Optional[float] = None     # best mass estimate (Jupiter masses)
    pl_dens: Optional[float] = None       # bulk density (g/cm³)
    pl_eqt: Optional[float] = None        # equilibrium temperature (K)
    pl_insol: Optional[float] = None      # insolation flux (Earth flux)

    # Transit parameters
    pl_trandep: Optional[float] = None    # transit depth (%)
    pl_trandur: Optional[float] = None    # transit duration (hours)

    # Detection method flags (0 or 1)
    tran_flag: Optional[int] = None
    rv_flag: Optional[int] = None
    ttv_flag: Optional[int] = None
    ima_flag: Optional[int] = None
    micro_flag: Optional[int] = None

    # Stellar parameters
    st_spectype: Optional[str] = None
    st_teff: Optional[float] = None       # effective temperature (K)
    st_mass: Optional[float] = None       # mass (Solar masses)
    st_rad: Optional[float] = None        # radius (Solar radii)
    st_met: Optional[float] = None        # metallicity (dex)
    st_logg: Optional[float] = None       # surface gravity log(cm/s²)
    st_lum: Optional[float] = None        # luminosity log(Solar)
    st_age: Optional[float] = None        # age (Gyr)

    # System
    sy_snum: Optional[int] = None         # number of stars in system
    sy_pnum: Optional[int] = None         # number of planets in system
    sy_dist: Optional[float] = None       # distance (pc)
    ra: Optional[float] = None            # right ascension (deg)
    dec: Optional[float] = None           # declination (deg)
