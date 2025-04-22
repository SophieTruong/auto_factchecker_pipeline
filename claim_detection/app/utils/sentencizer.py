import spacy

nlp = spacy.load("fi_core_news_md")
config = {"punct_chars": [".", "?", "!", "...", '."', '!"', '?"']}
nlp.add_pipe("sentencizer", config=config)

def get_sentences(text: str) -> list[str]:
    """
    Get the sentences from the text.
    """
    doc = nlp(text)
    return [sent.text for sent in doc.sents]


