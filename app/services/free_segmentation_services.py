# app/services.py

import os
import shutil
import uuid
from fastapi import UploadFile 
from fastapi.responses import FileResponse
from app.models.segmentation_model import ModelConfig
# from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
import aiofiles
import asyncio

from dotenv import dotenv_values

UPLOAD_DIR = "./uploads"
MODEL_DIR = "./models"
PREDICT_DIR = "./predictions"
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

async def save_and_upload_file(file: UploadFile, local_path: str, blob_path: str, content_type: str, container_client):
    # Save file locally
    async with aiofiles.open(local_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    # Upload to Azure
    await container_client.upload_blob(
        blob_path,
        content,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )

async def upload_data_service(images: list[UploadFile], masks: list[UploadFile], csv_file: UploadFile):
    session_id = str(uuid.uuid4())
    session_path = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)

    image_dir = os.path.join(session_path, "images")
    mask_dir = os.path.join(session_path, "masks")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)

    # Initialize Azure Blob client
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    try:
        if not await container_client.exists():
            await container_client.create_container()
    except Exception as e:
        print(f"Error checking/creating container: {e}")
        raise

    upload_tasks = []

    # Upload images
    for image in images:
        local_path = os.path.join(image_dir, image.filename)
        blob_path = f"semantic-images/{session_id}/images/{image.filename}"
        upload_tasks.append(
            await save_and_upload_file(image, local_path, blob_path, image.content_type, container_client)
        )

    # Upload masks
    for mask in masks:
        local_path = os.path.join(mask_dir, mask.filename)
        blob_path = f"semantic-images/{session_id}/masks/{mask.filename}"
        upload_tasks.append(
            await save_and_upload_file(mask, local_path, blob_path, mask.content_type, container_client)
        )
        
    # Upload CSV
    csv_local_path = os.path.join(session_path, "image_mask_mapping.csv")
    async with aiofiles.open(csv_local_path, "wb") as out_file:
        csv_content = await csv_file.read()
        await out_file.write(csv_content)
        
    blob_path = f"semantic-images/{session_id}/image_mask_mapping.csv"
    upload_tasks.append(
        await container_client.upload_blob(
            blob_path,
            csv_content,
            overwrite=True,
            content_settings=ContentSettings(content_type="text/csv")
        )
    )
    # Wait for all uploads
    await asyncio.gather(*upload_tasks)

    print('=====uploaded to Azure=====')
    return {"session_id": session_id, "status": "uploaded to Azure"}

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
