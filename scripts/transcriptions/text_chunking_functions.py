import spacy

nlp = spacy.load('en_core_web_sm')

def split_into_sentences(text_path: str = None, chunk: str = None):
    """
    Split text (from a file or raw string) into individual sentences using spaCy.

    Args:
        text_path (str, optional): Path to a .txt transcript file.
        chunk (str, optional): Raw text string to chunk.

    Returns:
        List[str]: List of cleaned sentence strings.

    Raises:
        ValueError: If both or neither of text_path and chunk are provided.
    """

    # Safety check: only one of the two inputs should be used
    if (text_path is None and chunk is None) or (text_path and chunk):
        raise ValueError("Provide exactly one of `text_path` or `chunk`.")

    # Load text from file
    if text_path:
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = chunk

    # Process with spaCy
    doc = nlp(text)

    # Extract sentences, strip whitespace, remove empties
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    return sentences


if __name__ == '__main__':
    text_path = 'downloads/transcriptions/nvidia_test.txt'
    sentences = split_into_sentences(text_path)
    print(sentences[:4])