import en_core_web_sm
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS

spacy_stopwords = STOP_WORDS
parser = English()
nlp = en_core_web_sm.load()

async def get_entities(message: str) -> list:
    doc = nlp(message)
    entities = [{'type': i.label_, 'value': str(i)} for i in doc.ents]    
    return entities

def spacy_tokenizer(message: str) -> list:
    tokens = nlp(message)
    cleaned_tokens = [(word.text, word.pos_, word.lemma_) for word in tokens if not word.is_stop and word.pos_ not in ('PUNCT')]
    return cleaned_tokens
