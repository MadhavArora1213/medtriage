
import asyncio
import random
import json
import os
import numpy as np
from typing import Dict, Any

from env.models import TriageObservation, TriageAction, StepResult
from env.reward import compute_reward
from env.graders import get_grader_for_task

class MedTriageEnv:
    def __init__(self, task_id: str = "task_01_basic_triage"):
        self.task_id = task_id
        self._state = None
        self._patient = None
        self._grader = get_grader_for_task(task_id)

    def _sample_patient(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if self.task_id == "task_01_basic_triage":
            file = "data/patients_easy.json"
        elif self.task_id == "task_02_differential":
            file = "data/patients_medium.json"
        else:
            file = "data/patients_hard.json"
            
        with open(os.path.join(base, file), "r") as f:
            patients = json.load(f)
        return random.choice(patients)

    async def reset(self) -> StepResult:
        self._patient = self._sample_patient()
        self._state = {
            "step_count": 0,
            "questions_asked": [],
            "tests_ordered": [],
            "red_flags": [],
            "test_results": {},
            "vitals_requested": [],
            "done": False,
        }
        return StepResult(observation=self._build_observation(), reward=0.0, done=False, info={})

    def _build_observation(self) -> TriageObservation:
        return TriageObservation(
            patient_id=self._patient["patient_id"],
            chief_complaint=self._patient["chief_complaint"],
            age=self._patient["age"],
            sex=self._patient["sex"],
            vitals=self._patient["vitals"],
            available_tests=["ECG", "CBC", "CXR", "Troponin", "BMP", "Lactate"],
            test_results=self._state["test_results"],
            red_flags_identified=self._state["red_flags"],
            questions_asked=self._state["questions_asked"],
            step_count=self._state["step_count"],
            max_steps=self._patient["max_steps"],
            episode_done=self._state["done"]
        )

    def _apply_action(self, action: TriageAction):
        a_type = action.action_type
        params = action.parameters
        
        if a_type == "ask_question":
            self._state["questions_asked"].append(params.get("question", ""))
        elif a_type == "order_test":
            test = params.get("test_name", "")
            self._state["tests_ordered"].append(test)
            self._state["test_results"][test] = "Result pending/simulated"
        elif a_type == "flag_critical":
            self._state["red_flags"].append(params.get("symptom", ""))
        elif a_type == "request_vitals":
            self._state["vitals_requested"].append(params.get("vital", ""))
            
    async def step(self, action: TriageAction) -> StepResult:
        if self._state["done"]:
            raise ValueError("Episode done.")
            
        self._state["step_count"] += 1
        reward, info = compute_reward(action, self._state, self._patient)
        self._apply_action(action)
        
        done = (action.action_type == "assign_triage" or self._state["step_count"] >= self._patient["max_steps"])
        self._state["done"] = done
        
        if done and action.action_type == "assign_triage":
            final = await self._grader(action, self._state, self._patient)
            reward += final * 0.6
            info["final_score"] = final
            info["true_esi"] = self._patient["true_esi"]
            
        return StepResult(
            observation=self._build_observation(),
            reward=float(np.clip(reward, 0.0, 1.0)),
            done=done,
            info=info
        )

    async def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "step_count": self._state["step_count"] if self._state else 0,
            "done": self._state["done"] if self._state else False
        }
