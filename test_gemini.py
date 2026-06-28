from ai.gemini_extractor import extract_medical_info

transcript = """
Patient has fever for 3 days.
BP 140/90.
History of diabetes.
Prescribed paracetamol.
CBC advised.
"""

data = extract_medical_info(transcript)

print(data)
print(type(data))