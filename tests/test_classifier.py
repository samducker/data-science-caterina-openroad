"""Test script for the genre classifier."""

from genre_classifier import initialize_classifier, classify_genre

def test_classifier():
    print("Initializing classifier...")
    classifier = initialize_classifier()
    
    test_titles = [
        "The Lord of the Rings",  # Should be fiction
        "How to Cook Everything",  # Should be non-fiction
        "Pride and Prejudice",    # Should be fiction
        "A Brief History of Time" # Should be non-fiction
    ]
    
    print("\nTesting classifier...")
    for title in test_titles:
        genre, confidence = classify_genre(classifier, title)
        print(f"\nTitle: '{title}'")
        print(f"Classification: {genre}")
        print(f"Confidence: {confidence:.2f}")

if __name__ == "__main__":
    test_classifier() 