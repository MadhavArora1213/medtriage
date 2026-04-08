import pytest
from env.reward import compute_reward
from env.models import TriageAction

def test_reward_ask_question():
    action = TriageAction(action_type="ask_question", parameters={"question": "Where is the pain?"})
    r, info = compute_reward(action, {}, {})
    assert r == 0.10

def test_reward_order_test_appropriate():
    action = TriageAction(action_type="order_test", parameters={"test_name": "ECG"})
    r, info = compute_reward(action, {}, {})
    assert r == 0.15

def test_reward_order_test_inappropriate():
    action = TriageAction(action_type="order_test", parameters={"test_name": "MRI of whole body"})
    r, info = compute_reward(action, {}, {})
    assert r == -0.10

def test_reward_flag_critical_correct():
    action = TriageAction(action_type="flag_critical", parameters={"symptom": "chest_pain"})
    patient = {"red_flags": ["chest_pain", "nausea"]}
    r, info = compute_reward(action, {}, patient)
    assert r == 0.20

def test_reward_flag_critical_incorrect():
    action = TriageAction(action_type="flag_critical", parameters={"symptom": "sore_throat"})
    patient = {"red_flags": ["chest_pain", "nausea"]}
    r, info = compute_reward(action, {}, patient)
    assert r == -0.10

def test_reward_request_vitals():
    action = TriageAction(action_type="request_vitals", parameters={"vital": "spo2"})
    r, info = compute_reward(action, {}, {})
    assert r == 0.05
