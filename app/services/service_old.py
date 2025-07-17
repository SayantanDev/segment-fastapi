# app/services.py

import os
import shutil
import uuid
from fastapi import UploadFile  # Add this import
from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.models.segmentation_model import ModelConfig
from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv
from dotenv import dotenv_values


UPLOAD_DIR = "./uploads"
MODEL_DIR = "./models"
PREDICT_DIR = "./predictions"
# load_dotenv()
dotenv_path = ".env"
config = dotenv_values(dotenv_path=dotenv_path, encoding="utf-8-sig")
for k, v in config.items():
    os.environ[k] = v

# # Azure setup
AZURE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_CONTAINER_NAME = os.environ["AZURE_CONTAINER_NAME"]
ACCOUNT_NAME = os.environ["AccountName"]
ACCOUNT_KEY = os.environ["AccountKey"]
ENDPOINT_SUFFIX = os.environ["EndpointSuffix"]


# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PREDICT_DIR, exist_ok=True)

async def upload_data_service(images: list[UploadFile], masks: list[UploadFile], csv_file: UploadFile):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    image_dir = os.path.join(session_path, "images")
    mask_dir = os.path.join(session_path, "masks")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)

    print("====AZURE_CONNECTION_STRING=====", AZURE_CONNECTION_STRING)
    print("====AZURE_CONTAINER_NAME=====", AZURE_CONTAINER_NAME)
    print("====ACCOUNT_NAME=====", ACCOUNT_NAME)
    print("====ACCOUNT_KEY=====", ACCOUNT_KEY)
    print("====ENDPOINT_SUFFIX=====", ENDPOINT_SUFFIX)

    # Save images
    for image in images:
        with open(os.path.join(image_dir, image.filename), "wb") as f:
            shutil.copyfileobj(image.file, f)

    # Save masks
    for mask in masks:
        with open(os.path.join(mask_dir, mask.filename), "wb") as f:
            shutil.copyfileobj(mask.file, f)

    # Save CSV file
    with open(os.path.join(session_path, "image_mask_mapping.csv"), "wb") as f:
        shutil.copyfileobj(csv_file.file, f)
    ####################################################################
    # folder name = customer_configs/config_xyz.yaml (antyhing you choose)
    ####################################################################

    return {"session_id": session_id, "status": "uploaded"}

async def train_model_service(config: ModelConfig, session_id: str):
    # Simulate training logic here or call a script
    model_path = os.path.join(MODEL_DIR, f"{session_id}.pth")
    with open(model_path, "w") as f:
        f.write("fake-model-weights")

    return {"status": "training_complete", "model_path": model_path}

async def predict_service(image: UploadFile, session_id: str):
    filename = f"{uuid.uuid4()}_{image.filename}"
    filepath = os.path.join(PREDICT_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Fake prediction logic
    output_mask = filepath.replace(".jpg", "_mask.png")
    shutil.copy(filepath, output_mask)

    return FileResponse(output_mask, media_type="image/png")
