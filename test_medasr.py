from transformers import pipeline
import huggingface_hub

# Download Google's sample audio
audio = huggingface_hub.hf_hub_download(
    repo_id="google/medasr",
    filename="test_audio.wav"
)

# Load MedASR
pipe = pipeline(
    "automatic-speech-recognition",
    model="google/medasr"
)

# Transcribe
result = pipe(
    audio,
    chunk_length_s=20,
    stride_length_s=2
)

print(result)