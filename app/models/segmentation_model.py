
from pydantic import BaseModel, EmailStr
from typing import Optional

class AugmentationParams(BaseModel):
    rotation: bool
    flip: bool
    brightness: bool
    contrast: bool

class ModelConfig(BaseModel):
    model_architecture: str
    backbone: str
    input_width: int
    input_height: int
    num_classes: int
    batch_size: int
    epochs: int
    learning_rate: float
    val_split: float
    optimizer: str
    loss_function: str
    data_aug: bool
    augmentation_params: AugmentationParams
    early_stopping: bool
    patience: int
    custom_notes: str

class TrainRequest(BaseModel):
    session_id: str
    config: ModelConfig