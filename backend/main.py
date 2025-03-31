import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime
from uuid import uuid4

# Models
class CurrentUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phone: str
    email: str

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phone: str
    content: str
    status: str = Field(default="pending")
    timestamp: datetime

class Call(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phone: str
    timestamp: datetime
    status: str = Field(default="pending")

class StatusUpdate(BaseModel):
    status: str

class SolicitudesResponse(BaseModel):
    solicitudes: List[dict]
    conversaciones_activas: List[dict]

app = FastAPI(debug=True)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


memory_db = {
    "messages": [],
    "calls": []
}

current_user: Optional[CurrentUser] = None

# Endpoints

# Retrieve all messages
@app.get("/messages", response_model=List[Message])
def get_messages():
    """Retrieve all messages."""
    return memory_db["messages"]

# Add a new message
@app.post("/messages", response_model=Message)
def add_message(message: Message):
    """Add a new message."""
    memory_db["messages"].append(message)
    return message

# Update a message's status
@app.put("/messages/{message_id}", response_model=Message)
def update_message_status(message_id: str, status_update: StatusUpdate):
    """Update the status of a specific message."""
    for message in memory_db["messages"]:
        if message.id == message_id:
            message.status = status_update.status
            return message
    raise HTTPException(status_code=404, detail="Message not found")

# Retrieve all calls
@app.get("/calls", response_model=List[Call])
def get_calls():
    """Retrieve all calls."""
    return memory_db["calls"]

# Add a new call
@app.post("/calls", response_model=Call)
def add_call(call: Call):
    """Add a new call."""
    memory_db["calls"].append(call)
    return call

# Update a call's status
@app.put("/calls/{call_id}", response_model=Call)
def update_call_status(call_id: str, status_update: StatusUpdate):
    """Update the status of a call."""
    for call in memory_db["calls"]:
        if call.id == call_id:
            call.status = status_update.status
            return call
    raise HTTPException(status_code=404, detail="Call not found")

# Retrieve solicitudes and conversaciones activas
@app.get("/solicitudes", response_model=SolicitudesResponse)
def get_solicitudes():
    """Retrieve solicitudes (pending) and conversaciones activas (accepted)."""
    # Filter pending items
    pending_messages = [msg.dict() for msg in memory_db["messages"] if msg.status == "pending"]
    pending_calls = [call.dict() for call in memory_db["calls"] if call.status == "pending"]

    # Filter accepted items
    accepted_messages = [msg.dict() for msg in memory_db["messages"] if msg.status == "accepted"]
    accepted_calls = [call.dict() for call in memory_db["calls"] if call.status == "accepted"]

    # Combine results
    solicitudes = pending_messages + pending_calls
    conversaciones_activas = accepted_messages + accepted_calls

    return {
        "solicitudes": solicitudes,
        "conversaciones_activas": conversaciones_activas,
    }

# Set the current user
@app.post("/current_user", response_model=CurrentUser)
def set_current_user(user: CurrentUser):
    """Set the current user."""
    global current_user
    current_user = user
    return current_user

# Get the current user
@app.get("/current_user", response_model=Union[CurrentUser, dict])
def get_current_user():
    """Retrieve the current user."""
    if current_user is None:
        raise HTTPException(status_code=404, detail="No current user set")
    return current_user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)