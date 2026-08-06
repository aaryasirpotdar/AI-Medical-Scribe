from database.database import db
from database.models import Patient, Consultation

def save_patient(data):
    print("Repository save_patient() called")
    patient = Patient(
        patient_name=data["Patient Name"],
        age=data["Age"],
        gender=data["Gender"],
        phone=data["Phone"]
    )

    db.session.add(patient)
    db.session.commit()

    consultation = Consultation(
        patient_id=patient.id,
        symptoms=data["Symptoms"],
        duration=data["Duration"],
        bp=data["BP"],
        history=data["Medical History"],
        medicines=data["Medicines"],
        tests=data["Tests"]
    )

    db.session.add(consultation)
    db.session.commit()

    return patient
