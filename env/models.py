from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class TriageObservation(BaseModel):
    patient_id: str
    chief_complaint: str  # "crushing chest pain, started 30 min ago"
    age: int
    sex: str  # "M" | "F" | "Other"
    vitals: Dict[str, float]  # {"hr": 118, "bp_sys": 88, "rr": 24, "spo2": 94, "temp": 38.9}
    available_tests: List[str]  # ["ECG", "CBC", "CXR", "Troponin", "BMP", "Lactate"]
    test_results: Dict[str, Any]  # Results of tests ordered so far
    red_flags_identified: List[str]
    questions_asked: List[str]
    step_count: int
    max_steps: int
    episode_done: bool

class TriageAction(BaseModel):
    action_type: str  # ask_question | order_test | flag_critical | assign_triage | request_vitals
    parameters: Dict[str, Any]  # {"question": "..."} | {"test_name": "ECG"} | {"level": 2}

class TriageReward(BaseModel):
    value: float  # Clipped to [-1.0, 1.0]
    components: Dict[str, float]  # Breakdown for debugging

class StepResult(BaseModel):
    observation: TriageObservation
    reward: float
    done: bool
    info: Dict[str, Any]
