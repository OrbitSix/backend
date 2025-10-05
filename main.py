from fastapi import FastAPI
from datamodel import ManualPredictionReq
from uuid import uuid4
from rabbitmq import RabbitMQ
import pika
import json
import redis

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
    rabbitmq = RabbitMQ()
    rabbitmq.channel.basic_publish(exchange="main-exchange",
                            routing_key="reasoning",
                            body=json.dumps({
                                    "id": req_id,
                                    **req_body.model_dump()
                                    }),
                            properties=pika.BasicProperties(delivery_mode=2)
                            )
    rabbitmq.close()

    # Return response
    return {
        "id": req_id,
        "verdict": res,
        "score": score,
    }


@app.get("/get-reason")
async def getReason(id:str):
    redisClient = redis.Redis(host="127.0.0.1", port=6379, db=1, decode_responses=True)
    reason = redisClient.get(id)
    redisClient.close()
    if reason == None:
        reason = ""
    return {
        "reason": reason
    }