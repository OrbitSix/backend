from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from datamodel import ManualPredictionReq
from uuid import uuid4
from rabbitmq import RabbitMQ
import pika
import json
import redis
import numpy as np
from model_reduced import prepare, predict
import shutil
from pathlib import Path
import os
import lightkurve as lk
import matplotlib.pyplot as plt
from fastapi.middleware.cors import CORSMiddleware

rabbitmq = RabbitMQ()
app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://orbitsix.earth"
]

app.add_middleware(CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prepare models
prepare()

# Light curves 
LIGHTCURVE_FOLDER = Path("lightcurvedata")


@app.post("/manual-predict") 
async def manualPrediction(req_body: ManualPredictionReq):
    # Parse the request body
    req_body_parsed = req_body.model_dump()

    # Generate prediction
    res = predict('manual', req_body_parsed)
    score = np.float64(0.0)
    if 'status' not in res:
        score = res["prediction"]["final_stacked_prob"]
    else:
        return {
            "verdict": "failed"
        }

    verdict = "Not Exoplanet"
    if score >= np.float64(0.5):
        verdict = "Exoplanet"

    # Generate UUID
    req_id = uuid4().__str__()
    
    # Pass reasoning job to MQ
    global rabbitmq
    if rabbitmq == None:
        rabbitmq = RabbitMQ()
    try:
        rabbitmq.channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    "type": 1,
                                    **req_body_parsed 
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                         )
    except:
        rabbitmq.close()
        rabbitmq = RabbitMQ()
        rabbitmq.channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    "type": 1,
                                    **req_body_parsed 
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                         )

    # Return response
    return {
        "id": req_id,
        "verdict": verdict,
        "score": score,
    }

@app.post("/raw-data")
async def rawLightcurvePrediction(file: UploadFile):
    # Generate UUID
    req_id = uuid4().__str__()

    # Fix file path and save file
    file_path = LIGHTCURVE_FOLDER / req_id
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Give the model the path and get prediction
    res = predict("raw", {
        "file_path": file_path,
    })
    score = np.float64(0.0)
    if 'status' not in res:
        score = res["prediction"]["final_stacked_prob"]
    else:
        return {
            "verdict": "failed"
        }

    verdict = "Not Exoplanet"
    if score >= np.float64(0.5):
        verdict = "Exoplanet"

    # Generate lightcurve plot
    lc = lk.read(file_path)

    # # Clean the data (remove NaNs, normalize flux)
    lc = lc.remove_nans().normalize()

    # # Plot the lightcurve
    fig, ax = plt.subplots(figsize=(8, 4))
    lc.plot(ax=ax, label="Lightcurve")

    # Customize the plot
    ax.set_title("Lightcurve from Raw Lightcurve Data")
    ax.set_xlabel("Time [days]")
    ax.set_ylabel("Normalized Flux")
    ax.legend()

    # Save as an image file (PNG)
    output_path = "lightcurveplot/"+req_id+".png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

    # Delete the file 
    os.remove(file_path)

    # Give reasoning job to MQ
    global rabbitmq
    if rabbitmq == None:
        rabbitmq = RabbitMQ()
    try:
        rabbitmq.channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    "type": 2,
                                    # **req_body_parsed 
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                         )
    except:
        rabbitmq.close()
        rabbitmq = RabbitMQ()
        rabbitmq.channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    "type": 2,
                                    # **req_body_parsed 
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                         )

    return {
        "id": req_id,
        "verdict": verdict,
        "score": score,
    }


@app.get("/reason")
async def getReason(id:str):
    redisClient = redis.Redis(host="127.0.0.1", port=6379, db=1, decode_responses=True)
    reason = redisClient.get(id)
    redisClient.close()
    if reason == None:
        reason = ""
    return {
        "reason": reason
    }

@app.get("/lightcurve")
async def getLightCurve(id:str):
    file_path = "lightcurveplot/"+id+".png"
    return FileResponse(file_path, media_type="image/png", filename="lightcurve.png")

@app.delete("/lightcurve")
async def getLightCurve(id:str):
    file_path = "lightcurveplot/"+id+".png"
    os.remove(file_path)
    return {
        "status": "ok"
    }