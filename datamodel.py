from pydantic import BaseModel

class ManualPredictionReq(BaseModel):
    # Planetary and Orbital Params
    radius_ratio: float
    planetary_radius: float
    orbital_period: float
    insolation_flux: float
    transit_depth: float
    transit_duration: float
    impact_parameter: float 
    transit_midpoint: float
    # Stellar Properties
    stellar_temp: float
    stellar_radius: float
    stellar_density: float
    stellar_mag_tess: float
    stellar_mass: float
    stellar_logg: float
    stellar_metallicity: float
    # Data Quality and Confidence
    transit_depth_err: float
    model_snr: float
