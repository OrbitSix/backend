from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from rabbitmq import RabbitMQ
import pika
import json

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

rabbitmq = RabbitMQ()
mq_channel = rabbitmq.channel
app = FastAPI()

@app.post("/manual-predict") 
async def manualPrediction(req_body: ManualPredictionReq):
    # Parse the request body
    print(req_body.model_dump())

    # Generate prediction
    score  = 0.93
    res = "Not Exoplanet"
    if score >= 0.65:
        res= "Exoplanet"

    # Generate UUID
    req_id = uuid4().__str__()
    
    # Pass reasoning job to MQ
    mq_channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    **req_body.model_dump()
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                            )

    # Return response
    return {
        "id": req_id,
        "verdict": res,
        "score": score,
    }


    
