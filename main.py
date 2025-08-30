"""
Stargate Simulation Web Backend - Task 1
FastAPI application with WebSocket support for real-time physics simulation
"""

print("=== STARGATE BACKEND STARTING - UVICORN VERSION ===", flush=True)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import asyncio
from typing import List
import uvicorn

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_simulation_config, validate_config
from dualportal import DualPortal
from logger import SimulationLogger
from hardware import TemperatureSensor, ContactSensor, TeslaBattery, FailsafeBlock

simulation_state = {
    "dual_portal": None,
    "config": None,
    "logger": None,
    "hardware": {
        "temp_sensor_1": TemperatureSensor("Portal1_Temp", -196.0),
        "temp_sensor_2": TemperatureSensor("Portal2_Temp", -196.0),
        "contact_sensor_1": ContactSensor("Portal1_Contact", True),
        "contact_sensor_2": ContactSensor("Portal2_Contact", True),
        "battery": TeslaBattery(),
        "failsafe": FailsafeBlock()
    },
    "running": False
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize simulation on startup"""
    try:
        config = load_simulation_config()
        validate_config(config)
        simulation_state["config"] = config
        simulation_state["logger"] = SimulationLogger()
        print("✓ Stargate Simulation API initialized successfully")
    except Exception as e:
        print(f"✗ Startup error: {e}")
    yield

app = FastAPI(title="Stargate Simulation API", version="1.0.0", lifespan=lifespan)

print("DEBUG: main.py loaded!", flush=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Stargate Simulation API", "status": "operational", "version": "uvicorn-fixed", "debug": "code-updated"}

@app.get("/api/status")
async def get_status():
    """Get current simulation status"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "not_initialized"}
    
    return {
        "status": "running" if simulation_state["running"] else "ready",
        "run_id": dp.run_id,
        "portal1": {
            "frequency": dp.portal1.freq,
            "stability": dp.portal1.stability,
            "energy": dp.portal1.energy,
            "safety": dp.portal1.safety_status
        },
        "portal2": {
            "frequency": dp.portal2.freq,
            "stability": dp.portal2.stability,
            "energy": dp.portal2.energy,
            "safety": dp.portal2.safety_status
        },
        "bridge": {
            "strength": dp.bridge_strength,
            "detune": dp.detune
        },
        "hardware": {
            "temp1": simulation_state["hardware"]["temp_sensor_1"].read(),
            "temp2": simulation_state["hardware"]["temp_sensor_2"].read(),
            "contact1": simulation_state["hardware"]["contact_sensor_1"].read(),
            "contact2": simulation_state["hardware"]["contact_sensor_2"].read(),
            "battery": simulation_state["hardware"]["battery"].status(),
            "failsafe": simulation_state["hardware"]["failsafe"].engaged
        }
    }

@app.post("/api/initialize")
async def initialize_simulation(payload_volume: float = 0.1, payload_mass: float = 75.0):
    """Initialize dual portal simulation"""
    try:
        config = simulation_state["config"]
        dp = DualPortal(
            freq1=config["resonance_frequency"],
            detune=config["detune_default"],
            power=config["energy_rate"]
        )
        
        hw = simulation_state["hardware"]
        dp.initialize_run(
            payload_volume=payload_volume,
            payload_mass=payload_mass,
            floor_temp1=hw["temp_sensor_1"].read(),
            floor_contact1=hw["contact_sensor_1"].read(),
            floor_temp2=hw["temp_sensor_2"].read(),
            floor_contact2=hw["contact_sensor_2"].read()
        )
        
        simulation_state["dual_portal"] = dp
        return {"status": "initialized", "run_id": dp.run_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/update_energy")
async def update_energy(dt: float = 1.0):
    """Update portal energy levels with real physics calculations"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        dp.portal1.update_energy(dt=dt)
        dp.portal2.update_energy(dt=dt)
        return {
            "status": "success",
            "portal1_energy": dp.portal1.energy,
            "portal2_energy": dp.portal2.energy,
            "dt": dt
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/form_bridge")
async def form_bridge(t: float = 1.0):
    """Form bridge between portals with real physics calculations"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        dp.form_bridge(t=t)
        return {
            "status": "success",
            "bridge_strength": dp.bridge_strength,
            "detune": dp.detune,
            "time": t
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/transfer_payload")
async def transfer_payload():
    """Attempt payload transfer with safety checks"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        result = dp.transfer_payload()
        logger = simulation_state["logger"]
        logger.log_event('API Transfer', dp.run_id, dp.portal1, dp.portal2, dp.bridge_strength, result)
        
        return {
            "status": "success",
            "transfer_result": result,
            "bridge_strength": dp.bridge_strength,
            "portal1_safety": dp.portal1.safety_status,
            "portal2_safety": dp.portal2.safety_status
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/update_parameters")
async def update_parameters(
    frequency1: float | None = None,
    frequency2: float | None = None,
    detune: float | None = None,
    power1: float | None = None,
    power2: float | None = None
):
    """Update simulation parameters with validation"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        config = simulation_state["config"]
        
        if frequency1 is not None:
            if 1.0 <= frequency1 <= 100.0:
                dp.portal1.freq = frequency1
            else:
                return {"status": "error", "message": "Frequency1 must be between 1-100 Hz"}
        
        if frequency2 is not None:
            if 1.0 <= frequency2 <= 100.0:
                dp.portal2.freq = frequency2
            else:
                return {"status": "error", "message": "Frequency2 must be between 1-100 Hz"}
        
        if detune is not None:
            if 0.01 <= detune <= 1.0:
                dp.detune = detune
            else:
                return {"status": "error", "message": "Detune must be between 0.01-1.0 Hz"}
        
        if power1 is not None:
            if 1000.0 <= power1 <= 15000.0:
                dp.portal1.power = power1
            else:
                return {"status": "error", "message": "Power1 must be between 1000-15000 W"}
        
        if power2 is not None:
            if 1000.0 <= power2 <= 15000.0:
                dp.portal2.power = power2
            else:
                return {"status": "error", "message": "Power2 must be between 1000-15000 W"}
        
        return {
            "status": "success",
            "portal1_freq": dp.portal1.freq,
            "portal2_freq": dp.portal2.freq,
            "detune": dp.detune,
            "portal1_power": dp.portal1.power,
            "portal2_power": dp.portal2.power
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/safety_status")
async def get_safety_status():
    """Get comprehensive safety monitoring data"""
    dp = simulation_state["dual_portal"]
    hw = simulation_state["hardware"]
    
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        return {
            "status": "success",
            "overall_safety": dp.portal1.safety_status and dp.portal2.safety_status,
            "portal1": {
                "safety_status": dp.portal1.safety_status,
                "stability": dp.portal1.stability,
                "floor_temp": dp.portal1.floor_temp,
                "floor_contact": dp.portal1.floor_contact,
                "temp_threshold": simulation_state["config"]["floor_temp_threshold"]
            },
            "portal2": {
                "safety_status": dp.portal2.safety_status,
                "stability": dp.portal2.stability,
                "floor_temp": dp.portal2.floor_temp,
                "floor_contact": dp.portal2.floor_contact,
                "temp_threshold": simulation_state["config"]["floor_temp_threshold"]
            },
            "hardware": {
                "battery_status": hw["battery"].status(),
                "failsafe_engaged": hw["failsafe"].engaged,
                "temp_sensor_1": hw["temp_sensor_1"].read(),
                "temp_sensor_2": hw["temp_sensor_2"].read(),
                "contact_sensor_1": hw["contact_sensor_1"].read(),
                "contact_sensor_2": hw["contact_sensor_2"].read()
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/export/csv")
async def export_csv():
    """Export simulation data as CSV"""
    logger = simulation_state["logger"]
    if not logger:
        return {"status": "error", "message": "Logger not initialized"}
    
    try:
        csv_data = logger.export_csv()
        return {
            "status": "success",
            "filename": logger.csv_filename,
            "data": csv_data,
            "format": "csv"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/export/json")
async def export_json():
    """Export audit trail as JSON"""
    logger = simulation_state["logger"]
    if not logger:
        return {"status": "error", "message": "Logger not initialized"}
    
    try:
        json_data = logger.export_json()
        return {
            "status": "success",
            "filename": logger.json_filename,
            "data": json_data,
            "format": "json"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/logs/events")
async def get_logged_events():
    """Get all logged simulation events"""
    logger = simulation_state["logger"]
    if not logger:
        return {"status": "error", "message": "Logger not initialized"}
    
    try:
        return {
            "status": "success",
            "records": logger.records,
            "record_count": len(logger.records)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/logs/audit")
async def get_audit_trail():
    """Get complete audit trail (same as records)"""
    logger = simulation_state["logger"]
    if not logger:
        return {"status": "error", "message": "Logger not initialized"}
    
    try:
        return {
            "status": "success",
            "audit_trail": logger.records,
            "audit_count": len(logger.records)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/logs/clear")
async def clear_logs():
    """Clear all logged data"""
    logger = simulation_state["logger"]
    if not logger:
        return {"status": "error", "message": "Logger not initialized"}
    
    try:
        logger.clear()
        return {
            "status": "success",
            "message": "All logs cleared"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/parameter_sweep")
async def parameter_sweep(base_energy: float = 1000, sweep_range: float = 1000, steps: int = 10):
    """Run parameter sweep optimization for bridge strength"""
    dp = simulation_state["dual_portal"]
    if not dp:
        return {"status": "error", "message": "Simulation not initialized"}
    
    try:
        results = []
        energy_step = (2 * sweep_range) / steps
        
        for i in range(steps):
            energy1 = base_energy - sweep_range + (i * energy_step)
            energy2 = base_energy - sweep_range + (i * energy_step)
            
            energy1 = max(100, min(20000, energy1))
            energy2 = max(100, min(20000, energy2))
            
            original_energy1 = dp.portal1.energy
            original_energy2 = dp.portal2.energy
            
            dp.portal1.energy = energy1
            dp.portal2.energy = energy2
            
            dp.form_bridge(t=1.0)
            bridge_strength = dp.bridge_strength
            
            results.append({
                "energy1": energy1,
                "energy2": energy2,
                "bridge_strength": bridge_strength,
                "detune": dp.detune,
                "step": i
            })
            
            dp.portal1.energy = original_energy1
            dp.portal2.energy = original_energy2
        
        return {
            "status": "success",
            "results": results,
            "best_result": max(results, key=lambda x: x["bridge_strength"]),
            "sweep_parameters": {
                "base_energy": base_energy,
                "sweep_range": sweep_range,
                "steps": steps
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time simulation data streaming"""
    await manager.connect(websocket)
    try:
        while True:
            dual_portal = simulation_state["dual_portal"]
            if dual_portal:
                simulation_data = {
                    "status": "running",
                    "run_id": dual_portal.run_id,
                    "portal1": {
                        "freq": dual_portal.portal1.freq,
                        "stability": dual_portal.portal1.stability,
                        "power": dual_portal.portal1.power,
                        "energy": dual_portal.portal1.energy,
                        "floor_temp": dual_portal.portal1.floor_temp,
                        "floor_contact": dual_portal.portal1.floor_contact,
                        "safety_status": dual_portal.portal1.safety_status,
                        "payload_volume": dual_portal.portal1.payload_volume,
                        "payload_mass": dual_portal.portal1.payload_mass,
                        "status_log": dual_portal.portal1.report_status()
                    },
                    "portal2": {
                        "freq": dual_portal.portal2.freq,
                        "stability": dual_portal.portal2.stability,
                        "power": dual_portal.portal2.power,
                        "energy": dual_portal.portal2.energy,
                        "floor_temp": dual_portal.portal2.floor_temp,
                        "floor_contact": dual_portal.portal2.floor_contact,
                        "safety_status": dual_portal.portal2.safety_status,
                        "payload_volume": dual_portal.portal2.payload_volume,
                        "payload_mass": dual_portal.portal2.payload_mass,
                        "status_log": dual_portal.portal2.report_status()
                    },
                    "bridge_strength": dual_portal.bridge_strength,
                    "transfer_energy": dual_portal.transfer_energy,
                    "detune": dual_portal.detune,
                    "status_log": dual_portal.status_log
                }
                await websocket.send_text(json.dumps(simulation_data))
            else:
                default_data = {
                    "status": "disconnected",
                    "portal1": None,
                    "portal2": None,
                    "bridge_strength": 0.0,
                    "transfer_energy": 0.0,
                    "detune": 0.0
                }
                await websocket.send_text(json.dumps(default_data))
            
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time log streaming"""
    await manager.connect(websocket)
    try:
        while True:
            logger = simulation_state["logger"]
            if logger:
                log_data = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "records": logger.records[-10:] if len(logger.records) > 10 else logger.records,
                    "record_count": len(logger.records)
                }
                await websocket.send_text(json.dumps(log_data))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
