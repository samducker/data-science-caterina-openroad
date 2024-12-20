"""Module for handling HuggingFace model interactions for genre classification."""

import torch
import traceback
from typing import Tuple, Optional
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from transformers.pipelines import Pipeline

def initialize_classifier() -> Optional[Pipeline]:
    """
    Initialize the zero-shot classification pipeline.
    
    Returns:
        Classification pipeline or None if initialization fails
    """
    try:
        print("Initializing model...")
        # Load model and tokenizer explicitly first
        model_name = "facebook/bart-large-mnli"
        
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print("Loading model...")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # Use float32 instead of float16
            device_map="auto"  # Let accelerate handle device mapping
        )
        
        # Set to eval mode
        model.eval()
        
        print("Creating classification pipeline...")
        classifier = pipeline(
            "zero-shot-classification",
            model=model,
            tokenizer=tokenizer,
            device_map="auto",  # Let accelerate handle device mapping
            batch_size=1  # Process one at a time
        )
        print("Model initialized successfully")
        return classifier
        
    except Exception as e:
        print(f"Failed to initialize classifier: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return None

def classify_genre(
    classifier: Pipeline,
    title: str,
    confidence_threshold: float = 0.6
) -> Tuple[str, float]:
    """
    Classify a book title as fiction or non-fiction using zero-shot classification.
    
    Args:
        classifier: HuggingFace pipeline object
        title: Book title to classify
        confidence_threshold: Minimum confidence threshold for classification
        
    Returns:
        Tuple of (genre, confidence_score)
    """
    try:
        print(f"\nClassifying: '{title}'")
        title_lower = title.lower()
        
        # Rule 1: Check for explicit format indicators
        format_indicators = {
            'non-fiction': ['guide', 'manual', 'handbook', 'textbook', 'cookbook', 'workbook', 
                          'encyclopedia', 'dictionary', 'reference', 'companion'],
            'fiction': ['novel', 'fiction', 'stories', 'tales']
        }
        
        for word in format_indicators['non-fiction']:
            if word in title_lower:
                print(f"Format indicator found (non-fiction): '{word}'")
                return ("non-fiction", 0.95)
                
        for word in format_indicators['fiction']:
            if word in title_lower:
                print(f"Format indicator found (fiction): '{word}'")
                return ("fiction", 0.95)
        
        # Rule 2: Check for subject matter that's clearly non-fiction
        nonfiction_subjects = [
            'history', 'biography', 'science', 'math', 'physics', 'chemistry',
            'geography', 'psychology', 'philosophy', 'economics', 'business',
            'self-help', 'self help', 'fitness', 'health', 'diet', 'nutrition',
            'exercise', 'workout', 'meditation', 'mindfulness', 'spirituality',
            'religion', 'politics', 'sociology', 'anthropology', 'archaeology',
            'medicine', 'engineering', 'technology', 'programming', 'computer',
            'investing', 'finance', 'money', 'career', 'leadership', 'management',
            'marketing', 'sales', 'entrepreneurship', 'kettlebell', 'yoga', 'pilates'
        ]
        
        for subject in nonfiction_subjects:
            if subject in title_lower:
                print(f"Subject matter indicator found (non-fiction): '{subject}'")
                return ("non-fiction", 0.95)
        
        # Rule 3: Check for instructional phrases
        instructional_phrases = [
            'how to', 'learn to', 'guide to', 'introduction to', 'basics of',
            'principles of', 'fundamentals of', 'essentials of', 'understanding',
            'mastering', 'complete', 'comprehensive', 'step by step', 'strategies',
            'techniques', 'methods', 'practices', 'lessons', 'skills', 'succeed in',
            'success in', 'master', 'improve your', 'boost your', 'enhance your',
            'transform your', 'optimize your', 'maximize your', 'for beginners',
            'for dummies', 'made easy', '101', 'basics', 'essentials'
        ]
        
        for phrase in instructional_phrases:
            if phrase in title_lower:
                print(f"Instructional phrase found: '{phrase}'")
                return ("non-fiction", 0.95)
        
        # Rule 4: Check for fiction genres/themes
        fiction_themes = [
            'dragon', 'sword', 'magic', 'wizard', 'witch', 'fairy', 'elf',
            'fantasy', 'adventure', 'mystery', 'thriller', 'romance', 'horror',
            'quest', 'journey', 'chronicles', 'saga', 'legend', 'myth', 'tale',
            'story', 'stories', 'enchanted', 'magical', 'supernatural', 'dystopian',
            'kingdom', 'prince', 'princess', 'warrior', 'hero', 'heroine'
        ]
        
        for theme in fiction_themes:
            if theme in title_lower:
                print(f"Fiction theme found: '{theme}'")
                return ("fiction", 0.95)
        
        # Rule 5: For remaining cases, use model with specific prompt
        input_text = (
            f"Book title: '{title}'. "
            "Analyze this title carefully. "
            "Question: Does this sound more like: "
            "1) A practical, educational, or informative book that teaches something specific, or "
            "2) A creative story meant for entertainment? "
            "Note: Most non-fiction titles are straightforward and describe their content directly."
        )
        
        candidate_labels = [
            "practical or educational book that teaches something specific",
            "creative story for entertainment"
        ]
        
        result = classifier(
            input_text,
            candidate_labels,
            hypothesis_template="This is a {}."
        )
        
        # Get the highest scoring label and its score
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        
        # Extract genre based on the label
        genre = "non-fiction" if "practical" in top_label else "fiction"
        
        print(f"Classification result: {genre} (confidence: {confidence:.2f})")
        
        if confidence < confidence_threshold:
            return ("unknown", confidence)
            
        return (genre, confidence)
        
    except Exception as e:
        print(f"Error classifying title '{title}': {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        return ("error", 0.0)
        
    finally:
        import gc
        gc.collect()