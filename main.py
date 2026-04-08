from fastapi import FastAPI, HTTPException
from env.environment import MedTriageEnv
from env.models import TriageAction, StepResult
import uuid

app = FastAPI(title="MedTriage-Env API")

# Store sessions in memory for simple hackathon environment
sessions = {}

@app.get("/")
async def root():
    return {"message": "MedTriage-Env: AI Medical Triage Environment is running."}

@app.get("/tasks")
async def list_tasks():
    return ["task_01_basic_triage", "task_02_differential", "task_03_critical_triage"]

@app.post("/reset")
async def reset(task_id: str = "task_01_basic_triage"):
    env = MedTriageEnv(task_id=task_id)
    session_id = str(uuid.uuid4())
    result = await env.reset()
    sessions[session_id] = env
    return {"session_id": session_id, "observation": result.observation}

@app.post("/step/{session_id}")
async def step(session_id: str, action: TriageAction):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = sessions[session_id]
    try:
        result = await env.step(action)
        if result.done:
            del sessions[session_id]
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state/{session_id}")
async def state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return await sessions[session_id].state()
