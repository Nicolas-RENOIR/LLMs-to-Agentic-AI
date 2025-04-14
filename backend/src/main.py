from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pipelines.generator_pipeline import run_pipeline
from pydantic import BaseModel
import base64

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI!"}

@app.post("/upload")
async def upload(text: str = Form(...), image: UploadFile = Form(...)):
    content = await image.read()
    image_base64 = base64.b64encode(content).decode('utf-8')
    run_pipeline(text, image_base64)
    
    return JSONResponse(content={"message": "Fichier et texte reçus avec succès !"})