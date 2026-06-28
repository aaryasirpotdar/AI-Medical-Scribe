from database.db import create_table, save_patient

create_table()

sample = {
    "Symptoms": ["fever"],
    "Duration": "3 days",
    "BP": "140/90",
    "Medical History": ["diabetes"],
    "Medicines": ["paracetamol"],
    "Tests": ["CBC"]
}

save_patient(sample)

print("Patient saved successfully!")