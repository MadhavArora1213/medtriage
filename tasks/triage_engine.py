# tasks/triage_engine.py
"""
Core Triage Assessment Engine using AI
"""
from typing import Literal
from models import PatientModel, TriageAssessmentModel, ESILevel
from datetime import datetime
import os

try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
    OpenAI = None

class TriageEngine:
    def __init__(self):
        if not openai_available:
            print("⚠️  WARNING: OpenAI module not installed. Running in demo mode (mock assessments)")
            self.client = None
            self.use_ai = False
            return
            
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip():
            try:
                self.client = OpenAI(api_key=api_key)
                self.use_ai = True
                print("✓ OpenAI client initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize OpenAI: {e}")
                self.client = None
                self.use_ai = False
        else:
            self.client = None
            self.use_ai = False
            print("⚠️  WARNING: OPENAI_API_KEY not set. Running in demo mode (mock assessments)")
        
        
    def assess_patient(self, patient: PatientModel) -> TriageAssessmentModel:
        """
        Assess patient using AI and clinical protocols
        """
        # Determine ESI level based on rules and AI analysis
        esi_level = self._calculate_esi_level(patient)
        
        # Generate AI explanation
        ai_explanation = self._generate_ai_assessment(patient, esi_level)
        
        # Get recommendations
        recommendations = self._get_recommendations(patient, esi_level)
        
        # Get diagnostic tests
        recommended_tests = self._get_recommended_tests(patient, esi_level)
        
        # Calculate confidence
        confidence = self._calculate_confidence(patient)
        
        severity_map = {
            1: 'Critical',
            2: 'Urgent', 
            3: 'Moderate',
            4: 'Minor',
            5: 'Non-urgent'
        }
        
        assessment = TriageAssessmentModel(
            patientId=patient.id,
            esiLevel=esi_level,
            severity=severity_map[esi_level],
            recommendedTests=recommended_tests,
            recommendations=recommendations,
            diagnosis=self._generate_diagnosis(patient),
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat(),
            aiExplanation=ai_explanation
        )
        
        return assessment
    
    def _calculate_esi_level(self, patient: PatientModel) -> ESILevel:
        """ESI Protocol Implementation"""
        
        # ESI-1: Resuscitation - High-risk situations
        high_risk_symptoms = ['Chest Pain', 'Shortness of Breath', 'Severe Headache']
        if any(sym in patient.symptoms for sym in high_risk_symptoms):
            if patient.vitals.heartRate > 120 or patient.vitals.temperature > 39:
                return 2
        
        # ESI-2: Emergent - Abnormal vitals
        if patient.vitals.heartRate > 130:
            return 2
        if patient.vitals.temperature > 40:
            return 2
            
        # ESI-3: Urgent - Stable but abnormal
        if len(patient.symptoms) >= 2:
            return 3
        if patient.vitals.temperature > 38.5:
            return 3
            
        # ESI-4: Less Urgent - Single minor symptom
        if len(patient.symptoms) == 1:
            return 4
            
        # ESI-5: Non-urgent
        return 5
    
    def _generate_ai_assessment(self, patient: PatientModel, esi_level: ESILevel) -> str:
        """Generate AI explanation using GPT or fallback"""
        if self.use_ai and self.client:
            try:
                prompt = f"""
As a medical AI assistant, assess this emergency room patient:

Patient: {patient.name}, Age: {patient.age}, Gender: {patient.gender}
Symptoms: {', '.join(patient.symptoms) if patient.symptoms else 'None reported'}
Vitals:
- Heart Rate: {patient.vitals.heartRate} bpm
- Temperature: {patient.vitals.temperature}°C
- Blood Pressure: {patient.vitals.bloodPressure}
- Respiratory Rate: {patient.vitals.respiratoryRate}

Medical History: {', '.join(patient.medicalHistory) if patient.medicalHistory else 'No prior history'}
Allergies: {', '.join(patient.allergies) if patient.allergies else 'None'}

Provide a brief clinical assessment (2-3 sentences) explaining the ESI-{esi_level} classification.
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"AI call failed, using fallback: {e}")
        
        # Fallback explanation
        return f"Patient requires ESI-{esi_level} assessment based on clinical presentation."
    
    def _get_recommendations(self, patient: PatientModel, esi_level: ESILevel) -> list:
        """Get clinical recommendations"""
        recommendations = []
        
        if esi_level <= 2:
            recommendations.append("Monitor vital signs every 15 minutes")
            recommendations.append("Establish IV line")
            
        if any(sym in patient.symptoms for sym in ['Chest Pain', 'Shortness of Breath']):
            recommendations.append("Apply oxygen if SpO2 < 94%")
            recommendations.append("Continuous cardiac monitoring")
            
        if patient.vitals.temperature > 39:
            recommendations.append("Antipyretic administration")
            recommendations.append("Hydration support")
            
        if esi_level >= 4:
            recommendations.append("Standard observation")
            
        return recommendations
    
    def _get_recommended_tests(self, patient: PatientModel, esi_level: ESILevel) -> list:
        """Get recommended diagnostic tests"""
        tests = []
        
        if any(sym in patient.symptoms for sym in ['Chest Pain', 'Shortness of Breath']):
            tests.extend(['ECG', 'Troponin Test', 'Chest X-Ray'])
            
        if patient.vitals.temperature > 38.5 or 'Fever' in patient.symptoms:
            tests.append('Blood Test')
            tests.append('Urinalysis')
            
        if 'Severe Headache' in patient.symptoms:
            tests.extend(['CT Scan', 'Lumbar Puncture'])
            
        if 'Abdominal Pain' in patient.symptoms:
            tests.append('Ultrasound')
            
        return list(set(tests))[:5]
    
    def _generate_diagnosis(self, patient: PatientModel) -> str:
        """Generate preliminary diagnosis"""
        if not patient.symptoms:
            return "No acute symptoms reported"
        
        # Simple rule-based diagnosis
        if 'Chest Pain' in patient.symptoms:
            return "Possible acute coronary syndrome - cardiac evaluation required"
        elif 'Shortness of Breath' in patient.symptoms:
            return "Respiratory distress - pulmonary assessment needed"
        elif 'Fever' in patient.symptoms:
            return "Febrile illness - infection workup indicated"
        elif 'Severe Headache' in patient.symptoms:
            return "Severe headache - neurological evaluation required"
        else:
            return f"Assessment based on presenting symptoms: {patient.symptoms[0]}"
    
    def _calculate_confidence(self, patient: PatientModel) -> float:
        """Calculate confidence score of assessment"""
        confidence = 0.7  # Base confidence
        
        # More complete data = higher confidence
        if patient.medicalHistory:
            confidence += 0.05
        if patient.vitals.temperature:
            confidence += 0.05
        if len(patient.symptoms) > 2:
            confidence += 0.1
            
        return min(confidence, 0.95)
