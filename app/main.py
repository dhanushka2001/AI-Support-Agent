import fastapi
from fastapi import FastAPI

import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"FastAPI version": fastapi.__version__,
            "Timestamp": datetime.datetime.now()
    }
