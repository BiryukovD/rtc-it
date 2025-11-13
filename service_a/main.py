from fastapi import FastAPI, Path, Request
from fastapi.responses import JSONResponse
import time
from shemas import Device

app = FastAPI()

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal provisioning exception"
        }
    )

equipment_ids = [
    "ABC123",
    "a1b2c3",
    "XYZ7890",
    "device01",
    "123456",
    "aB12Cd34"
]

@app.post('/api/v1/equipment/cpe/{id}')
def configuring_equipment(device: Device, id: str = Path(..., regex="^[a-zA-Z0-9]{6,}$")):
    if id in equipment_ids:
        time.sleep(60)
        return {
            'code': 200,
            'message': 'success'
        }
    else:
        return JSONResponse(
            status_code=404,
            content={"code": 404, "message": "The requested equipment is not found"}
        )

