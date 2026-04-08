# tasks/models.py
"""
Data models for MedTriage-Env
Using built-in Python types for Python 3.14 compatibility (Pydantic wheels not available)
"""
from typing import List, Optional, Literal, Dict, Any

ESILevel = Literal[1, 2, 3, 4, 5]

class PatientModel:
    """Patient data model"""
    def __init__(self, id: str, name: str, age: int, gender: Literal['M', 'F', 'Other'],
                 symptoms: List[str], vitals: Dict[str, Any], medicalHistory: Optional[List[str]] = None,
                 allergies: Optional[List[str]] = None, currentMedications: Optional[List[str]] = None,
                 createdAt: Optional[str] = None):
        self.id = id
        self.name = name
        self.age = age
        self.gender = gender
        self.symptoms = symptoms or []
        self.vitals = vitals
        self.medicalHistory = medicalHistory or []
        self.allergies = allergies or []
        self.currentMedications = currentMedications or []
        self.createdAt = createdAt
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'symptoms': self.symptoms,
            'vitals': self.vitals,
            'medicalHistory': self.medicalHistory,
            'allergies': self.allergies,
            'currentMedications': self.currentMedications,
            'createdAt': self.createdAt
        }


class TriageAssessmentModel:
    """AI Triage Assessment Result"""
    def __init__(self, patientId: str, esiLevel: ESILevel, 
                 severity: Literal['Critical', 'Urgent', 'Moderate', 'Minor', 'Non-urgent'],
                 recommendedTests: List[str], recommendations: List[str], diagnosis: str,
                 confidence: float, timestamp: str, aiExplanation: str):
        self.patientId = patientId
        self.esiLevel = esiLevel
        self.severity = severity
        self.recommendedTests = recommendedTests or []
        self.recommendations = recommendations or []
        self.diagnosis = diagnosis
        self.confidence = confidence
        self.timestamp = timestamp
        self.aiExplanation = aiExplanation
    
    def to_dict(self):
        return {
            'patientId': self.patientId,
            'esiLevel': self.esiLevel,
            'severity': self.severity,
            'recommendedTests': self.recommendedTests,
            'recommendations': self.recommendations,
            'diagnosis': self.diagnosis,
            'confidence': self.confidence,
            'timestamp': self.timestamp,
            'aiExplanation': self.aiExplanation
        }


class TriageCaseModel:
    """Complete triage case"""
    def __init__(self, id: str, patient: Dict, assessment: Dict, 
                 status: Literal['pending', 'in_progress', 'completed'],
                 score: int = 0, reward: int = 0):
        self.id = id
        self.patient = patient
        self.assessment = assessment
        self.status = status
        self.score = score
        self.reward = reward
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient,
            'assessment': self.assessment,
            'status': self.status,
            'score': self.score,
            'reward': self.reward
        }


class APIResponse:
    """Standard API Response"""
    def __init__(self, success: bool, data: Optional[Dict] = None, 
                 error: Optional[str] = None, message: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.message = message
    
    def to_dict(self):
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'message': self.message
        }
