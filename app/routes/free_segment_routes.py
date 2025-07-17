# app/routes.py

from fastapi import APIRouter, UploadFile, File, Form
from app.models.segmentation_model import TrainRequest
from app.db.connection import db
from app.services.free_segmentation_services import upload_data_service, train_model_service, predict_service
from passlib.context import CryptContext

free_segment_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# ===============================================================================
@free_segment_router.get("/test")
def read_test():
    return {"message": "This is a test route!"}
# ===============================================================================
@free_segment_router.post("/upload")
async def upload_data(
    images: list[UploadFile] = File(...),
    masks: list[UploadFile] = File(...),
    csv_file: UploadFile = File(...)
):
    return await upload_data_service(images, masks, csv_file)
# ===============================================================================
@free_segment_router.post("/train")
async def train_model(request: TrainRequest):
    return await train_model_service(request.config, request.session_id)
# ===============================================================================
@free_segment_router.post("/predict")
async def predict(image: UploadFile = File(...), session_id: str = Form(...)):
    return await predict_service(image, session_id)
# ================================================================================
