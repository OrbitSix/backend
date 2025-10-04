from pydantic import BaseModel

class ManualPredictionReq(BaseModel):
    # Planetary and Orbital Params
    k_ror: float
    pl_prad_re: float
    pl_orbper_days: float
    pl_insol_flux: float
    pl_depth_ppm: float
    pl_trandur_hrs: float
    koi_impact: float 
    pl_tranmid_bjd: float
    # Stellar Properties
    st_teff_k: float
    st_rad_rsun: float
    k_srho: float
    st_mag_tess: float
    # Data Quality and Confidence
    koi_model_snr: float
