import spacy

nlp = spacy.load('en_core_web_sm')

def split_into_sentences(text_path):
    """
    Load text from file and split it into individual sentences using spaCy.

    Args:
        text_path (str): Path to the .txt transcript file.

    Returns:
        List[str]: List of sentence strings.
    """
    with open(text_path, "r", encoding='utf-8') as f:
        text = f.read()

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    return sentences


if __name__ == '__main__':
    text_path = 'downloads/transcriptions/nvidia_test.txt'
    sentences = split_into_sentences(text_path)
    print(sentences[:4])