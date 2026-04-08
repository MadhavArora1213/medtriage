
def compute_reward(action, state, patient):
    action_type = action.action_type
    params = action.parameters
    
    r = 0.0
    info = {}
    
    if action_type == 'ask_question':
        r += 0.10
        info['reason'] = 'asked question'
    elif action_type == 'order_test':
        test_name = params.get('test_name', '')
        if test_name in ['ECG', 'CBC']:
            r += 0.15
            info['reason'] = 'appropriate test'
        else:
            r -= 0.10
            info['reason'] = 'inappropriate test'
    elif action_type == 'flag_critical':
        symptom = params.get('symptom', '')
        if symptom in patient.get('red_flags', []):
            r += 0.20
            info['reason'] = 'correct red flag'
        else:
            r -= 0.10
            info['reason'] = 'incorrect red flag'
    elif action_type == 'request_vitals':
        r += 0.05
        info['reason'] = 'requested vital'
            
    return r, info
