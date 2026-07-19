from transformers import AutoProcessor, AutoModelForCTC
import torch
import librosa

print("Loading MedASR...")

MODEL_ID = "google/medasr"

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(MODEL_ID)

model = AutoModelForCTC.from_pretrained(
    MODEL_ID
).to(device)

model.eval()

print("MedASR Loaded Successfully!")


def transcribe_audio(audio_path):

    print("Loading:", audio_path)

    audio, sample_rate = librosa.load(
        audio_path,
        sr=16000,
        mono=True
    )

    print(audio.shape)

    inputs = processor(
        audio,
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True
    )

    inputs = inputs.to(device)

    with torch.no_grad():
        predicted_ids = model.generate(**inputs)

    transcript = processor.batch_decode(
        predicted_ids,
        skip_special_tokens=True
    )[0]

    return transcript