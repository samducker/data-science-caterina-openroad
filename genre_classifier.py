"""Simple module for fiction/non-fiction classification using HuggingFace."""

import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from transformers.pipelines import Pipeline
from typing import Tuple, Optional

def initialize_classifier() -> Optional[Pipeline]:
    """Initialize the zero-shot classification pipeline."""
    try:
        model_name = "facebook/bart-large-mnli"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map="auto"
        )
        model.eval()
        
        classifier = pipeline(
            "zero-shot-classification",
            model=model,
            tokenizer=tokenizer,
            device_map="auto"
        )
        return classifier
        
    except Exception as e:
        print(f"Failed to initialize classifier: {str(e)}")
        return None

def classify_genre(classifier: Pipeline, title: str) -> Tuple[str, float]:
    """Classify a book title as fiction or non-fiction.
    
    Args:
        classifier: HuggingFace pipeline object
        title: Book title to classify
        
    Returns:
        Tuple of (genre, confidence_score)
    """
    try:
        # Create a more descriptive input text
        input_text = f"Book title: {title}"
        
        # Define more specific labels
        candidate_labels = [
            "a fictional story or novel",
            "a non-fiction book or educational material"
        ]
        
        result = classifier(
            input_text,
            candidate_labels=candidate_labels,
            hypothesis_template="This text is about {}"
        )
        
        # Map the result to our desired output format
        genre = "Fiction" if "fictional" in result['labels'][0] else "Non-Fiction"
        confidence = result['scores'][0]
        
        return (genre, confidence)
        
    except Exception as e:
        print(f"Error classifying title '{title}': {str(e)}")
        return ("error", 0.0)