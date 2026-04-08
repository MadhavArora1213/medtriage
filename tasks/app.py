# tasks/app.py
"""
MedTriage-Env Backend API
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models import PatientModel, APIResponse, TriageAssessmentModel
from triage_engine import TriageEngine

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Triage Engine
triage_engine = TriageEngine()

# In-memory storage (use database in production)
patients_db = {}
cases_db = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MedTriage-Env Backend',
        'version': '1.0.0'
    })


@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create new patient record"""
    try:
        data = request.get_json()
        patient = PatientModel(
            id=data.get('id'),
            name=data.get('name'),
            age=data.get('age'),
            gender=data.get('gender', 'M'),
            symptoms=data.get('symptoms', []),
            vitals=data.get('vitals', {}),
            medicalHistory=data.get('medicalHistory', []),
            allergies=data.get('allergies', []),
            currentMedications=data.get('currentMedications', []),
            createdAt=data.get('createdAt')
        )
        
        patients_db[patient.id] = patient
        
        response = APIResponse(
            success=True,
            data=patient.to_dict(),
            message="Patient record created successfully"
        )
        
        return jsonify(response.to_dict()), 201
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/patients', methods=['GET'])
def list_patients():
    """List all patients"""
    try:
        patients = [p.to_dict() for p in patients_db.values()]
        response = APIResponse(
            success=True,
            data=patients
        )
        return jsonify(response.to_dict()), 200
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get specific patient"""
    try:
        patient = patients_db.get(patient_id)
        if not patient:
            response = APIResponse(
                success=False,
                error="Patient not found"
            )
            return jsonify(response.to_dict()), 404
        
        response = APIResponse(
            success=True,
            data=patient.to_dict()
        )
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/triage/assess', methods=['POST'])
def assess_triage():
    """Perform triage assessment on patient"""
    try:
        data = request.get_json()
        patient_id = data.get('patientId')
        
        patient = patients_db.get(patient_id)
        if not patient:
            response = APIResponse(
                success=False,
                error="Patient not found"
            )
            return jsonify(response.to_dict()), 404
        
        # Run triage assessment
        assessment = triage_engine.assess_patient(patient)
        
        # Store case
        case_id = f"case_{patient_id}_{int(__import__('time').time())}"
        case = {
            'id': case_id,
            'patient': patient.to_dict(),
            'assessment': assessment.to_dict(),
            'status': 'completed',
            'score': 100,
            'reward': 50
        }
        cases_db[case_id] = case
        
        response = APIResponse(
            success=True,
            data=assessment.to_dict(),
            message="Triage assessment completed"
        )
        
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/triage/case/<case_id>', methods=['GET'])
def get_triage_case(case_id):
    """Get specific triage case"""
    try:
        case = cases_db.get(case_id)
        if not case:
            response = APIResponse(
                success=False,
                error="Case not found"
            )
            return jsonify(response.to_dict()), 404
        
        response = APIResponse(
            success=True,
            data=case
        )
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/triage/cases', methods=['GET'])
def list_triage_cases():
    """List all triage cases"""
    try:
        cases = list(cases_db.values())
        response = APIResponse(
            success=True,
            data=cases
        )
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/triage/cases', methods=['POST'])
def create_or_update_case():
    """Create new case or update existing case with action"""
    try:
        data = request.get_json()
        patient_id = data.get('patientId')
        patient_data = data.get('patient')  # Full patient object
        assessment = data.get('assessment')
        action = data.get('action', 'submitted')
        
        if not patient_id or not assessment:
            response = APIResponse(
                success=False,
                error="Missing patientId or assessment"
            )
            return jsonify(response.to_dict()), 400
        
        # Create case
        case_id = f"case_{patient_id}_{int(__import__('time').time())}"
        case = {
            'id': case_id,
            'patientId': patient_id,
            'patient': patient_data if patient_data else {'id': patient_id},  # Store full patient data
            'assessment': assessment,
            'status': 'completed' if action == 'approved' else 'review_requested' if action == 'review_requested' else 'submitted',
            'action': action,
            'score': 100,
            'reward': 50 if action == 'approved' else 25,
            'createdAt': __import__('datetime').datetime.now().isoformat()
        }
        cases_db[case_id] = case
        
        response = APIResponse(
            success=True,
            data=case,
            message=f"Case {action} successfully"
        )
        
        return jsonify(response.to_dict()), 201
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'totalPatients': len(patients_db),
            'totalCases': len(cases_db),
            'avgReward': sum([c.get('reward', 0) for c in cases_db.values()]) / max(len(cases_db), 1)
        }
        response = APIResponse(
            success=True,
            data=stats
        )
        return jsonify(response.to_dict()), 200
        
    except Exception as e:
        response = APIResponse(
            success=False,
            error=str(e)
        )
        return jsonify(response.to_dict()), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    response = APIResponse(
        success=False,
        error="Endpoint not found"
    )
    return jsonify(response.to_dict()), 404


if __name__ == '__main__':
    # Development mode
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
