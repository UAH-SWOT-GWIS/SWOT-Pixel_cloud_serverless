from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.download import download_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello from SWOT"}

@app.post("/download")
async def download(short_name: str, 
    granules: list[str], date_range: list[str] | None = None, 
    bounding_box: list[float] | None = None, version: str | None = None):

    response = await download_data(short_name, granules, date_range, bounding_box, version)

    return JSONResponse(content = response)
