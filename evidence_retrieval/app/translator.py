from deep_translator import GoogleTranslator
from langdetect import detect

def translate_claim(claim: str):
    language = detect(claim)
    if language != 'fi':
        return GoogleTranslator(source='auto', target='fi').translate(claim)
    return claim
