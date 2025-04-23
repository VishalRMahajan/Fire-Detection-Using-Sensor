import asyncio
import json
import logging
from typing import List, Dict
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data Models
class SensorReading(BaseModel):
    temperature: float  # Temperature in Celsius
    humidity: float     # Humidity in percentage
    smoke_level: int    # Smoke sensor analog reading (0–1023)
    fire_detected: bool # Whether fire is detected based on logic
    
    # Optional fields for location & flame detection
    flame_detected: bool = False  # Optional: Whether the flame sensor detected fire (1 = detected)
    latitude: float = 0.0         # Latitude of the sensor location
    longitude: float = 0.0        # Longitude of the sensor location

    class Config:
        extra = "allow"


# WebSocket Connection Management
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sensor_history: List[Dict] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, data: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                self.disconnect(connection)

    def store_sensor_data(self, data: Dict):
        if len(self.sensor_history) >= 100:
            self.sensor_history.pop(0)
        self.sensor_history.append(data)


# FastAPI Application
app = FastAPI(title="Sensor Monitoring System")
connection_manager = ConnectionManager()

# Templates and Static Files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_dashboard(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/fire-alert")
async def get_fire_alert(request: Request):
    """Get fire alert HTML component when fire is detected"""
    if not connection_manager.sensor_history:
        return {"message": "No sensor data available"}
    
    latest_reading = connection_manager.sensor_history[-1]
    
    if latest_reading.get("fire_detected", False):
        return templates.TemplateResponse(
            "fire_alert.html", 
            {
                "request": request,
                "temperature": latest_reading.get("temperature"),
                "humidity": latest_reading.get("humidity"),
                "smoke_level": latest_reading.get("smoke_level"),
                "latitude": latest_reading.get("latitude", 0.0),
                "longitude": latest_reading.get("longitude", 0.0),
                "timestamp": latest_reading.get("timestamp", "Unknown")
            }
        )
    return {"message": "No fire detected"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                
                reading = SensorReading(**data)
                
                if "timestamp" not in data:
                    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                

                connection_manager.store_sensor_data(data)
                
                logger.info(f"Sensor Reading: {reading}")
                
                await connection_manager.broadcast(data)
                
            except ValueError as ve:
                logger.error(f"Data Validation Error: {ve}")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

@app.get("/sensor-history")
async def get_sensor_history():
    """Retrieve recent sensor readings"""
    return connection_manager.sensor_history

@app.get("/current-status")
async def get_current_status():
    """Get the most recent sensor reading"""
    if connection_manager.sensor_history:
        return connection_manager.sensor_history[-1]
    return {"message": "No sensor data available"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )