
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re 
from difflib import SequenceMatcher
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")


def get_medicine_vocabulary() -> list[str]:
    """Load the clinic-maintained medicine names used for correction."""

    vocabulary_path = Path(__file__).resolve().parent.parent / "medical_vocabulary.json"
    try:
        with vocabulary_path.open(encoding="utf-8") as file:
            medicines = json.load(file).get("medicines", [])
        return [medicine for medicine in medicines if isinstance(medicine, str)]
    except (OSError, json.JSONDecodeError):
        return []


def get_relevant_medicine_candidates(transcript: str, limit: int = 12) -> list[str]:
    """Find likely medicine names locally before asking Gemini to choose."""

    words = re.findall(r"[a-z0-9]+", transcript.casefold())
    if not words:
        return []

    spoken_phrases = []
    for size in range(1, min(4, len(words)) + 1):
        spoken_phrases.extend("".join(words[index:index + size]) for index in range(len(words) - size + 1))

    scored = []
    for medicine in get_medicine_vocabulary():
        normalized_medicine = re.sub(r"[^a-z0-9]", "", medicine.casefold())
        score = max(
            SequenceMatcher(None, phrase, normalized_medicine).ratio()
            for phrase in spoken_phrases
        )
        scored.append((score, medicine))

    return [medicine for _, medicine in sorted(scored, reverse=True)[:limit]]


def collapse_exact_repetition(text: str) -> str:
    """Remove consecutive duplicate words and fully repeated phrases."""

    original_words = text.split()
    deduplicated_words = []
    previous_word = None
    for word in original_words:
        normalized_word = re.sub(r"^\W+|\W+$", "", word).casefold()
        if normalized_word and normalized_word == previous_word:
            continue
        deduplicated_words.append(word)
        previous_word = normalized_word

    original_words = deduplicated_words
    words = [re.sub(r"^\W+|\W+$", "", word).casefold() for word in original_words]
    for size in range(1, len(words) // 2 + 1):
        if len(words) % size:
            continue
        phrase = words[:size]
        if phrase * (len(words) // size) == words:
            return " ".join(original_words[:size]).rstrip(" ,.;:")
    return text


def correct_medical_transcript(transcript: str, category: str) -> str:
    """Correct and separate clearly distinct items from a Whisper transcript."""

    if not transcript.strip() or not os.getenv("GEMINI_API_KEY"):
        return transcript

    whisper_words = transcript.split()
    prompt = f"""
STRICT OUTPUT CONTRACT: check every numbered Whisper word and return ONLY JSON
in this exact format: {{"words": ["word 1", "word 2"]}}.

Return exactly {len(whisper_words)} strings: one single-word output for each
input word, in the same order. Never add, remove, combine, split, or reorder
words. Keep a word unchanged unless its correction is highly certain. Do not
guess or invent clinical information. If any instruction below conflicts with
this contract, follow this contract.

You are a conservative medical transcription editor. Return ONLY the corrected
transcript—no explanation, labels, markdown, or quotation marks.

The transcript came from an English clinical recording in the category:
{category}

Correct a medication name, dosage, symptom, diagnosis, or test only when that
single token can be corrected with high confidence. If any word is uncertain,
preserve the original token.

Do not split the recording into separate items or lines.

Numbered Whisper words:
{json.dumps(list(enumerate(whisper_words, start=1)), ensure_ascii=False)}
"""

    try:
        response = model.generate_content(prompt)
        text = re.sub(r"```(?:json)?|```", "", response.text).strip()
        corrected_words = json.loads(text).get("words")

        valid_word_list = (
            isinstance(corrected_words, list)
            and len(corrected_words) == len(whisper_words)
            and all(
                isinstance(word, str) and word.strip() and len(word.split()) == 1
                for word in corrected_words
            )
        )
        if not valid_word_list:
            return transcript

        return " ".join(word.strip() for word in corrected_words)
    # Gemini is optional. Its API/network/quota failures must not discard a
    # successful Whisper transcription.
    except Exception:
        return transcript


def split_medical_transcript(transcript: str, category: str) -> str:
    """Return one line per clearly distinct item in the selected category."""

    if not transcript.strip() or not os.getenv("GEMINI_API_KEY"):
        return transcript

    medicine_candidates = (
        ", ".join(get_relevant_medicine_candidates(transcript))
        if category.strip().casefold() == "medicines"
        else "Not applicable for this category"
    )
    prompt = f"""
Return ONLY valid JSON in this exact shape: {{"items": ["item"]}}.
You are a conservative medical transcription editor.
Category: {category}
Transcript: {transcript}

Separate clearly distinct symptoms, medicines, tests, diagnoses, or history
items. Example: "fever, cold and cough" becomes ["fever", "cold", "cough"].
Correct a medical word only when its spoken wording and category make it highly
likely; never invent facts. For BP and Duration, normally return one item.

For the Medicines category, use these approved medicine names as correction
candidates: {medicine_candidates}. Prefer an approved candidate only when the
sound strongly matches it; otherwise preserve the original wording.
"""

    try:
        response = model.generate_content(prompt)
        text = re.sub(r"```(?:json)?|```", "", response.text).strip()
        items = json.loads(text).get("items")
        if not isinstance(items, list):
            return transcript
        clean_items = []
        seen_items = set()
        for item in items:
            if not isinstance(item, str) or not item.strip():
                continue
            cleaned_item = collapse_exact_repetition(item.strip())
            duplicate_key = " ".join(cleaned_item.casefold().split())
            if duplicate_key not in seen_items:
                seen_items.add(duplicate_key)
                clean_items.append(cleaned_item)
        return "\n".join(clean_items) or transcript
    except Exception:
        return transcript


def extract_medical_info(transcript):

    prompt = f"""
    Extract the following information from the medical transcript:

    - Symptoms
    - Duration
    - BP
    - Medical History
    - Medicines
    - Tests

    Return ONLY JSON.

    Transcript:
    {transcript}
    """

    response = model.generate_content(prompt)

    # DEBUG
    print("\n===== RAW GEMINI RESPONSE =====")
    print(response.text)
    print("===============================\n")

    text = response.text

    text = re.sub(r"```json|```", "", text).strip()

    data = json.loads(text)

    print("EXTRACTED DATA:")
    print(data)

    return data
