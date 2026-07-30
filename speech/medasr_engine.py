"""Robust medical transcription with Whisper and a medical vocabulary prompt."""

import os

import torch
import whisper


# Use Whisper's English-only medium model for stronger word recognition.
# It is slower and uses more memory than "small"; set WHISPER_MODEL=small if
# a faster CPU-only experience is more important than accuracy.
MODEL_NAME = os.getenv("WHISPER_MODEL", "medium.en")
BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
MEDICAL_PROMPT = (
    "azithromycin, telmisartan, levocetirizine, paracetamol, ibuprofen, "
    "amoxicillin, metformin, pantoprazole, CBC, blood pressure"
)

print(f"Loading Whisper {MODEL_NAME} for medical transcription...")
model = whisper.load_model(MODEL_NAME)
print("Whisper loaded successfully!")


def transcribe_audio(audio_path: str) -> str:
    """Transcribe a recording using English and medical context."""

    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        initial_prompt=MEDICAL_PROMPT,
        # FP16 is substantially faster on NVIDIA GPUs; CPU inference must use
        # normal precision.
        fp16=torch.cuda.is_available(),
        # Beam search considers several candidate word sequences instead of
        # accepting Whisper's first guess.
        beam_size=BEAM_SIZE,
        patience=1.0,
        # Each browser recording is an independent short clip. Reusing prior
        # decoder text can cause loops such as the same medicine repeated.
        condition_on_previous_text=False,
        temperature=0,
    )
    return " ".join(result["text"].split())
