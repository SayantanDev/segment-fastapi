# app/routes.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.models import TrainRequest
from app.services import upload_data_service, train_model_service, predict_service

router = APIRouter()

@router.get("/test")
def read_test():
    return {"message": "This is a test route!"}

@router.post("/upload")
async def upload_data(
    images: list[UploadFile] = File(...),
    masks: list[UploadFile] = File(...),
    csv_file: UploadFile = File(...)
):
    return await upload_data_service(images, masks, csv_file)

@router.post("/train")
async def train_model(request: TrainRequest):
    return await train_model_service(request.config, request.session_id)

@router.post("/predict")
async def predict(image: UploadFile = File(...), session_id: str = Form(...)):
    return await predict_service(image, session_id)
