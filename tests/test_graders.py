import pytest
import asyncio
from env.graders import grader_01_basic, grader_02_differential, grader_03_critical
from env.models import TriageAction

@pytest.mark.anyio
async def test_grader_01_exact_match():
    action = TriageAction(action_type="assign_triage", parameters={"level": 2})
    patient = {"true_esi": 2}
    score = await grader_01_basic(action, {}, patient)
    assert score == 1.0

@pytest.mark.anyio
async def test_grader_01_off_by_one():
    action = TriageAction(action_type="assign_triage", parameters={"level": 3})
    patient = {"true_esi": 2}
    score = await grader_01_basic(action, {}, patient)
    assert score == 0.5

@pytest.mark.anyio
async def test_grader_02_differential():
    action = TriageAction(action_type="assign_triage", parameters={"level": 2})
    state = {"red_flags": ["chest_pain"], "tests_ordered": ["ECG"]}
    patient = {"true_esi": 2, "red_flags": ["chest_pain"]}
    score = await grader_02_differential(action, state, patient)
    # accuracy (1.0 * 0.5) + red_flag (1.0 * 0.2) + test (0.5 * 0.3) = 0.5 + 0.2 + 0.15 = 0.85
    assert score == 0.85

@pytest.mark.anyio
async def test_grader_03_critical_score():
    action = TriageAction(action_type="assign_triage", parameters={"level": 1})
    state = {"step_count": 4, "tests_ordered": ["ECG"]}
    patient = {"true_esi": 1}
    score = await grader_03_critical(action, state, patient)
    # accuracy (1.0 * 0.8) + speed (1.0 * 0.2) - 0.0 penalty = 1.0
    assert score == 1.0

@pytest.mark.anyio
async def test_grader_03_critical_penalty():
    action = TriageAction(action_type="assign_triage", parameters={"level": 1})
    state = {"step_count": 10, "tests_ordered": ["ECG", "CBC", "CXR"]}
    patient = {"true_esi": 1}
    score = await grader_03_critical(action, state, patient)
    # accuracy (1.0 * 0.8) + speed (0.5 * 0.2) - 0.2 test penalty = 0.8 + 0.1 - 0.2 = 0.7
    assert round(score, 2) == 0.7
