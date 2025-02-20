from deep_translator import GoogleTranslator
from langdetect import detect

def translate_claim(claim: str, target_language: str = "fi"):
    try:
        language = detect(claim)
        if language != target_language:
            return GoogleTranslator(source=language, target=target_language).translate(claim)
    except Exception as e:
        print(f"Error translating claim: {e}")
        return claim
