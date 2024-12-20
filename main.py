"""Main script for classifying book genres and updating Google Sheets."""

import os
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from sheets_operations import get_service, read_book_titles, write_genres
from genre_classifier import initialize_classifier, classify_genre

def validate_env() -> Dict[str, str]:
    """Validate and return environment variables."""
    required = {
        'GOOGLE_CREDENTIALS_PATH': 'credentials.json',
        'SPREADSHEET_ID': None,
        'SHEET_RANGE': 'Sheet1!A2:A'
    }
    
    config = {}
    for var, default in required.items():
        if not (value := os.getenv(var, default)):
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config

def process_books(service, classifier, spreadsheet_id: str, sheet_range: str) -> None:
    """Process books and update their genres."""
    if not (books := read_book_titles(service, spreadsheet_id, sheet_range)):
        print("No books found to process")
        return
    
    print(f"\nProcessing {len(books)} books...")
    current_batch: List[Tuple[str, str]] = []
    processed = updated = 0
    
    for title, row in books:
        sheet_name = sheet_range.split('!')[0]
        genre_range = f"{sheet_name}!F{row}"
        
        print(f"\nProcessing: '{title}'")
        
        # Check existing genre
        try:
            existing = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=genre_range
            ).execute()
            
            if (existing.get('values', [['']])[0][0].strip() and 
                existing['values'][0][0].lower() != 'unknown'):
                print(f"Skipping - genre exists: '{existing['values'][0][0]}'")
                continue
        except Exception as e:
            print(f"Error checking genre: {e}")
            continue
        
        # Classify genre
        try:
            genre, confidence = classify_genre(classifier, title)
            if genre != "error":
                current_batch.append((genre_range, genre))
                print(f"Classified as: {genre} (confidence: {confidence:.2f})")
            
            # Write batch if size limit reached
            if len(current_batch) >= 10:
                if write_genres(service, spreadsheet_id, current_batch):
                    updated += len(current_batch)
                current_batch = []
            
            processed += 1
            if processed % 10 == 0:
                print(f"\nProgress: {processed}/{len(books)} books")
                
        except Exception as e:
            print(f"Error processing '{title}': {e}")
            continue
    
    # Write remaining updates
    if current_batch and write_genres(service, spreadsheet_id, current_batch):
        updated += len(current_batch)
    
    print(f"\nComplete: {processed} processed, {updated} updated")

def main() -> None:
    """Entry point of the script."""
    try:
        load_dotenv()
        config = validate_env()
        
        if not (service := get_service(config['GOOGLE_CREDENTIALS_PATH'])):
            print("Failed to initialize Google Sheets service")
            return
            
        if not (classifier := initialize_classifier()):
            print("Failed to initialize genre classifier")
            return
        
        process_books(service, classifier, config['SPREADSHEET_ID'], config['SHEET_RANGE'])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 