from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

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


app = FastAPI()

@app.post("/manual-predict") 
async def manualPrediction(req_body: ManualPredictionReq):
    # Parse the request body
    print(req_body.model_dump())
    # Generate prediction
    
    # Generate UUID
    req_id = uuid4()
    print("Req Id:", req_id.__str__())
    # Pass reasoning job to MQ

    # Return response
    return {
        "verdict": "Exoplanet",
        "score": 0.93,
    }