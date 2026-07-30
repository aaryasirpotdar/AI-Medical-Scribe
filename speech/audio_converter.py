import subprocess
import os


def convert_to_wav(input_path):

    output_path = os.path.splitext(input_path)[0] + ".wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",          # Mono
        "-ar", "16000",      # MedASR's expected sample rate
        "-sample_fmt", "s16",
        "-af", "highpass=f=80",  # Remove handling/room rumble
        output_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return output_path
