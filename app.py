from flask import Flask, render_template, request, send_file
from database.db import (
    create_table,
    save_patient,
    get_all_patients,
    search_patients
)
import os
from speech.whisper_engine import transcribe_audio
from ai.gemini_extractor import extract_medical_info
from reports.report_generator import generate_report
from reports.pdf_generator import generate_pdf

app = Flask(__name__)

create_table()

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        audio = request.files["audio"]

        filename = audio.filename

        filepath = os.path.join(
        "uploads",
        filename
        )

        audio.save(filepath)

        text = transcribe_audio(filepath)

        data = extract_medical_info(text)

        print(data)

        for key, value in data.items():
            print(key, type(value), value)

        

        print("Patient saved successfully!")

        # print("AFTER GEMINI:", data)
        # print("BEFORE REVIEW:", data)
        # print("FROM FORM:", request.form)

     

        return render_template(
            "review.html",
            data=data
        )
        
    return render_template("index.html")

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
    # print("AFTER GEMINI:", data)
    # print("BEFORE REVIEW:", data)
    # print("FROM FORM:", request.form)

    return render_template("report.html", data=data)

@app.route("/download-pdf")
def download_pdf():

    return send_file(
        "patient_report.pdf",
        as_attachment=True
    )

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