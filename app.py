from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

import os
import uuid
import tempfile
from speech.audio_converter import convert_to_wav

from database.db import (
    create_table,
    save_patient,
    get_all_patients,
    search_patients
)

from speech.medasr_engine import transcribe_audio
from ai.gemini_extractor import extract_medical_info

from reports.pdf_generator import generate_pdf

app = Flask(__name__)

create_table()

UPLOAD_FOLDER = "uploads/consultation_audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("consultation.html")


# -------------------------
# Record Small Audio Clip
# -------------------------
@app.route("/record", methods=["POST"])
def record():

    audio = request.files["audio"]
    category = request.form["category"]

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False
    ) as temp:

        audio.save(temp.name)

        wav_path = convert_to_wav(temp.name)

        transcript = transcribe_audio(wav_path)
        print("=" * 50)
        print("RAW MEDASR TRANSCRIPT")
        print(transcript)
        print("=" * 50)

    try:
        os.remove(temp.name)
        os.remove(wav_path)
    except OSError:
        pass

    return jsonify({

    "category": category,
    "transcript": transcript

})


# -------------------------
# Generate Structured Report
# -------------------------
@app.route("/generate", methods=["POST"])
def generate():

    consultation = request.json

    grouped = {
        "Symptoms": [],
        "Duration": [],
        "BP": [],
        "Medical History": [],
        "Medicines": [],
        "Tests": [],
        "Diagnosis": [],
        "Examination": []
    }

    for entry in consultation["entries"]:
        grouped[entry["category"]].append(entry["text"])

    # Convert list -> string
    for key in grouped:
        grouped[key] = "\n".join(grouped[key])

    grouped["Patient Name"] = consultation["name"]
    grouped["Age"] = consultation["age"]
    grouped["Gender"] = consultation["gender"]
    grouped["Phone"] = consultation.get("phone", "")

    # Optional Gemini refinement
    grouped = extract_medical_info(grouped)

    return render_template(
        "review.html",
        data=grouped
    )


# -------------------------
# Save Final Report
# -------------------------
@app.route("/save", methods=["POST"])
def save():

    patient_name = request.form["patient_name"]
    age = request.form["age"]
    gender = request.form["gender"]
    phone = request.form["phone"]

    data = {

        "Symptoms": request.form.get("symptoms", ""),
        "Duration": request.form.get("duration", ""),
        "BP": request.form.get("bp", ""),
        "Medical History": request.form.get("medical_history", ""),
        "Medicines": request.form.get("medicines", ""),
        "Tests": request.form.get("tests", "")

    }

    data["Patient Name"] = patient_name
    data["Age"] = age
    data["Gender"] = gender
    data["Phone"] = phone

    save_patient(data)

    generate_pdf(data)

    return render_template(
        "report.html",
        data=data
    )


# -------------------------
# Download PDF
# -------------------------
@app.route("/download-pdf")
def download_pdf():

    return send_file(
        "patient_report.pdf",
        as_attachment=True
    )


# -------------------------
# Dashboard
# -------------------------
@app.route("/dashboard")
def dashboard():

    search = request.args.get("search", "")

    if search:
        patients = search_patients(search)
    else:
        patients = get_all_patients()

    return render_template(
        "dashboard.html",
        patients=patients,
        search=search
    )


if __name__ == "__main__":
    app.run(debug=True)