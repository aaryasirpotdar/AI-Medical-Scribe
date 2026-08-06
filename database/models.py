from database.database import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    consultations = db.relationship(
        "Consultation",
        backref="patient",
        lazy=True
    )


class Consultation(db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False
    )

    symptoms = db.Column(db.Text)
    duration = db.Column(db.String(100))
    bp = db.Column(db.String(20))
    history = db.Column(db.Text)
    medicines = db.Column(db.Text)
    tests = db.Column(db.Text)
    transcript = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
