from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.free_segment_routes import free_segment_router
from app.routes.auth_routes import auth_router

app = FastAPI()

# Allow CORS from local frontend (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Access-Token", "X-Refresh-Token"],
)

# Include the routes
app.include_router(auth_router, prefix="/auth")
app.include_router(free_segment_router, prefix="/freeSegmentation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
