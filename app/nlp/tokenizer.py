def tokenize(text: str) -> list:
    """
    Splits cleaned text into individual word tokens
    and removes stop words.
    """
    if not text:
        return []

    # Common stop words to remove
    stop_words = set([
        "the", "a", "an", "and", "or", "but", "in",
        "on", "at", "to", "for", "of", "with", "was",
        "is", "it", "he", "she", "they", "then", "that",
        "this", "were", "had", "has", "have", "been",
        "when", "where", "which", "while", "after",
        "before", "during", "from", "into", "about"
    ])

    # Split text into words
    words = text.split()

    # Remove stop words but keep risk-related words
    tokens = [
        word for word in words
        if word not in stop_words
        and len(word) > 2
    ]

    return tokens