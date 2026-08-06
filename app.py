from config import Config
from database.database import db
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    abort
)
from werkzeug.utils import secure_filename

import os
import uuid
import tempfile
from speech.audio_converter import convert_to_wav

from database.db import (
    create_table,
    get_all_patients,
    search_patients
)

from database.repository import save_patient

from speech.medasr_engine import transcribe_audio
from ai.gemini_extractor import correct_medical_transcript, split_medical_transcript

from reports.pdf_generator import generate_pdf

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

#create_table()

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

    audio = request.files.get("audio")
    category = request.form.get("category", "")

    if audio is None or not audio.filename:
        return jsonify({"error": "An audio recording is required."}), 400

    if not category:
        return jsonify({"error": "A consultation category is required."}), 400

    with tempfile.NamedTemporaryFile(
        suffix=".webm",
        delete=False
    ) as temp:

        audio.save(temp.name)

        wav_path = None
        try:
            wav_path = convert_to_wav(temp.name)
            transcript = transcribe_audio(wav_path)
            transcript = correct_medical_transcript(transcript, category)
            transcript = split_medical_transcript(transcript, category)
        except Exception:
            app.logger.exception("Medical transcription failed")
            return jsonify({"error": "Unable to transcribe this recording."}), 500
        finally:
            for path in (temp.name, wav_path):
                if path:
                    try:
                        os.remove(path)
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
        "Allergies": [],
        "Medical History": [],
        "Medicines": [],
        "Tests": [],
        "Diagnosis": [],
        "Examination": []
    }

    for entry in consultation["entries"]:
        category = entry.get("category")
        text = entry.get("text", "").strip()
        if category in grouped and text:
            grouped[category].append(text)

    # Convert list -> string
    for key in grouped:
        grouped[key] = "\n".join(grouped[key])

    grouped["Patient Name"] = consultation["name"]
    grouped["Age"] = consultation["age"]
    grouped["Gender"] = consultation["gender"]
    grouped["Phone"] = consultation.get("phone", "")

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
        "Allergies": request.form.get("allergies", ""),
        "Medical History": request.form.get("medical_history", ""),
        "Medicines": request.form.get("medicines", ""),
        "Tests": request.form.get("tests", ""),
        "Diagnosis": request.form.get("diagnosis", ""),
        "Examination": request.form.get("examination", "")

    }

    data["Patient Name"] = patient_name
    data["Age"] = age
    data["Gender"] = gender
    data["Phone"] = phone

    save_patient(data)

    safe_name = secure_filename(patient_name.strip()) or "patient"
    pdf_filename = f"{safe_name}.pdf"
    pdf_path = os.path.join("reports", pdf_filename)
    os.makedirs("reports", exist_ok=True)
    generate_pdf(data, pdf_path)

    return render_template(
        "report.html",
        data=data,
        pdf_filename=pdf_filename
    )


# -------------------------
# Download PDF
# -------------------------
@app.route("/download-pdf")
def download_pdf():

    filename = secure_filename(request.args.get("filename", ""))
    if not filename or not filename.lower().endswith(".pdf"):
        abort(404)

    pdf_path = os.path.join("reports", filename)
    if not os.path.isfile(pdf_path):
        abort(404)

    return send_file(
        pdf_path,
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
