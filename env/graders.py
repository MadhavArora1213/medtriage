
def clamp_score(score):
    # Meta Validator requirement: strictly between 0 and 1
    return max(0.01, min(0.99, float(score)))

async def grader_01_basic(action, state, patient):
    level = action.parameters.get('level')
    if level == patient.get('true_esi'):
        return clamp_score(1.0)
    elif abs(level - patient.get('true_esi')) == 1:
        return clamp_score(0.5)
    return clamp_score(0.0)

async def grader_02_differential(action, state, patient):
    level = action.parameters.get('level')
    accuracy = 1.0 if level == patient.get('true_esi') else 0.0
    
    red_flag_score = 0.0
    p_flags = set(patient.get('red_flags', []))
    if p_flags:
        identified = set(state.get('red_flags', []))
        red_flag_score = len(p_flags.intersection(identified)) / len(p_flags)
    else:
        red_flag_score = 1.0
        
    test_score = 0.5 if len(state.get('tests_ordered', [])) > 0 else 0.0
    return clamp_score((accuracy * 0.5) + (red_flag_score * 0.2) + (test_score * 0.3))

async def grader_03_critical(action, state, patient):
    level = action.parameters.get('level')
    steps = state.get('step_count', 15)
    
    accuracy = 1.0 if level == patient.get('true_esi') else 0.0
    test_penalty = 0.2 if len(state.get('tests_ordered', [])) > 2 else 0.0
    speed_score = 1.0 if steps <= 5 else max(0.0, 1.0 - ((steps - 5) * 0.1))
    
    return clamp_score((accuracy * 0.8) + (speed_score * 0.2) - test_penalty)

def get_grader_for_task(task_id: str):
    if task_id == "task_01_basic_triage":
        return grader_01_basic
    elif task_id == "task_02_differential":
        return grader_02_differential
    elif task_id == "task_03_critical_triage":
        return grader_03_critical
    return grader_01_basic
