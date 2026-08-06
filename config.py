import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/medical_scribe"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False