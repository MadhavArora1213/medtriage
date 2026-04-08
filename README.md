---
title: MedTriage OpenEnv
emoji: 🚑
colorFrom: red
colorTo: gray
sdk: docker
app_port: 7860
---

# MedTriage-Env: AI Medical Triage Decision Environment

MedTriage-Env is a high-fidelity OpenEnv environment designed to evaluate AI agents on clinical decision-making and emergency department triage.

## 🚑 Environment Description
Agents act as a Triage Nurse in an Emergency Room. They must assess synthetic patient presentations, identify life-threatening conditions (red flags), order appropriate diagnostics, and assign an ESI (Emergency Severity Index) level from 1 (Most Urgent) to 5 (Least Urgent).

## 🚀 Key Features
- **Real-World Task**: Based on the standard Emergency Severity Index (ESI) used in hospitals.
- **Spec Compliance**: Full implementation of OpenEnv `step()`, `reset()`, and `state()` APIs.
- **Multiple Tasks**: Progressively harder scenarios (Easy, Medium, Hard).
- **Dense Rewards**: Signal-rich reward function with partial progress tracking.

## 🛠 Action Space
The agent can perform the following actions:
- `ask_question(question: str)`: Gather history from the patient.
- `order_test(test_name: str)`: Order labs like ECG, CBC, or Troponin.
- `flag_critical(symptom: str)`: Identify a critical red flag.
- `request_vitals(vital: str)`: Review specific physiological data.
- `assign_triage(level: int)`: Final ESI classification (Ends episode).

## 👁 Observation Space
Returns a structured state including:
- `patient_id`, `age`, `sex`, `chief_complaint`
- `vitals`: (Heart Rate, Blood Pressure, SpO2, etc.)
- `test_results`: Data from ordered diagnostics.
- `red_flags_identified`: History of flagged symptoms.
- `step_count` and `max_steps`.

## 📈 Tasks & Grading
1. **task_01_basic_triage (Easy)**: Clear presentation (e.g., mild cold). Goal: Assign ESI 4 or 5.
2. **task_02_differential (Medium)**: Ambiguous chest/abdominal pain. Requires diagnostic testing.
3. **task_03_critical_triage (Hard)**: Life-threats (Sepsis/STEMI). Must identify within 5 steps.

Graders verify the accuracy of the triage level and the appropriateness of the diagnostic process.

## 💻 Setup & Inference
### 1. Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Inference
```bash
python inference.py
```

## 🐳 Docker Deployment
Built for Hugging Face Spaces:
```bash
docker build -t medtriage-env .
docker run -p 7860:7860 medtriage-env
```
