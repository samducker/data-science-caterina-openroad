"""Main script for classifying book genres and updating Google Sheets."""

import os
import time
from typing import List, Tuple, Dict
from dotenv import load_dotenv

from sheets_operations import get_service, read_book_titles, write_genres
from genre_classifier import initialize_classifier, classify_genre

def validate_environment() -> Dict[str, str]:
    """
    Validate all required environment variables are present and of correct type.
    
    Returns:
        Dictionary containing validated environment variables
        
    Raises:
        ValueError: If any required variable is missing or invalid
    """
    required_vars = {
        'GOOGLE_CREDENTIALS_PATH': 'credentials.json',  # default value
        'SPREADSHEET_ID': None,  # no default, must be provided
        'SHEET_RANGE': 'Sheet1!A2:A'  # default value
    }
    
    config: Dict[str, str] = {}
    
    for var_name, default_value in required_vars.items():
        value = os.getenv(var_name, default_value)
        if value is None:
            raise ValueError(f"Required environment variable {var_name} is not set")
        
        # Additional type/format validation
        if var_name == 'SPREADSHEET_ID' and not value.strip():
            raise ValueError("SPREADSHEET_ID cannot be empty")
        
        if var_name == 'SHEET_RANGE':
            if '!' not in value or not value.strip():
                raise ValueError("SHEET_RANGE must be in format 'Sheet1!A2:A'")
        
        config[var_name] = value
    
    return config

def process_books(
    credentials_path: str,
    spreadsheet_id: str,
    sheet_range: str,
    confidence_threshold: float = 0.85,  # Very high threshold for model-based classification
    batch_size: int = 10,  # Process 10 books at a time
    max_retries: int = 2  # Maximum number of retries for unknown genres
) -> bool:
    """
    Main function to process books and update their genres.
    
    Args:
        credentials_path: Path to Google Sheets credentials file
        spreadsheet_id: ID of the target spreadsheet
        sheet_range: A1 notation of the range containing book titles
        confidence_threshold: Minimum confidence for genre classification
        batch_size: Number of books to process before writing to sheet
        max_retries: Maximum number of retries for unknown genres
        
    Returns:
        Boolean indicating overall success of the operation
    """
    try:
        # Initialize Google Sheets service
        service = get_service(credentials_path)
        if not service:
            print("Failed to initialize Google Sheets service")
            return False
            
        # Initialize HuggingFace classifier
        print("\nInitializing HuggingFace classifier...")
        classifier = initialize_classifier()
        if not classifier:
            print("Failed to initialize genre classifier")
            return False
            
        # Read book titles
        print("\nReading book titles from sheet...")
        books = read_book_titles(service, spreadsheet_id, sheet_range)
        if not books:
            print("No books found to process")
            return False
            
        print(f"\nFound {len(books)} books to process")
        
        # Process books in batches
        current_batch: List[Tuple[str, str]] = []
        total_processed = 0
        total_updated = 0
        
        for title, row, column in books:
            try:
                # Add delay to avoid rate limits
                time.sleep(1)
                
                sheet_name = sheet_range.split('!')[0]
                genre_column = 'F'
                genre_range = f"{sheet_name}!{genre_column}{row}"
                
                print(f"\n--- Processing '{title}' ---")
                print(f"Title in column {column}, checking genre in column {genre_column}")
                print(f"Checking cell: {genre_range}")
                
                try:
                    existing_genre = service.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=genre_range
                    ).execute()
                    
                    has_value = (
                        'values' in existing_genre and
                        existing_genre['values'] and
                        existing_genre['values'][0] and
                        existing_genre['values'][0][0].strip() != ''
                    )
                    
                    if has_value:
                        value = existing_genre['values'][0][0].strip()
                        if value.lower() == 'unknown':
                            print(f"Found 'unknown' genre - will reclassify")
                        else:
                            print(f"Skipping '{title}' - genre already exists: '{value}'")
                            continue
                        
                except Exception as e:
                    print(f"Error checking genre for '{title}': {str(e)}")
                    continue
                
                # Classify with retries for unknown results
                genre = "unknown"
                confidence = 0.0
                retries = 0
                
                while genre == "unknown" and retries < max_retries:
                    if retries > 0:
                        print(f"\nRetrying classification (attempt {retries + 1}/{max_retries})")
                        time.sleep(1)  # Brief delay between retries
                        
                    try:
                        genre, confidence = classify_genre(
                            classifier,
                            title,
                            confidence_threshold
                        )
                    except Exception as e:
                        print(f"Error during classification attempt {retries + 1}: {str(e)}")
                        break
                        
                    retries += 1
                
                if genre == "error":
                    print(f"Skipping '{title}' due to classification error")
                    continue
                    
                if genre == "unknown":
                    print(f"Still unknown after {max_retries} attempts")
                
                current_batch.append((genre_range, genre))
                print(f"Final classification for '{title}': {genre} (confidence: {confidence:.2f})")
                
                # Write batch if it reaches the size limit
                if len(current_batch) >= batch_size:
                    if write_genres(service, spreadsheet_id, current_batch):
                        total_updated += len(current_batch)
                        print(f"\nWrote batch of {len(current_batch)} updates")
                    current_batch = []
                
                total_processed += 1
                if total_processed % 10 == 0:
                    print(f"\nProgress: {total_processed}/{len(books)} books processed")
                
            except Exception as e:
                print(f"Error processing '{title}': {str(e)}")
                continue
        
        # Write any remaining updates
        if current_batch:
            if write_genres(service, spreadsheet_id, current_batch):
                total_updated += len(current_batch)
                print(f"\nWrote final batch of {len(current_batch)} updates")
        
        print(f"\nProcessing complete:")
        print(f"Total books processed: {total_processed}")
        print(f"Total genres updated: {total_updated}")
        
        return True
            
    except Exception as e:
        print(f"Unexpected error in process_books: {str(e)}")
        return False

def main() -> None:
    """Entry point of the script."""
    load_dotenv()
    
    try:
        # Validate environment variables
        config = validate_environment()
        
        success = process_books(
            config['GOOGLE_CREDENTIALS_PATH'],
            config['SPREADSHEET_ID'],
            config['SHEET_RANGE']
        )
        
        if not success:
            print("Script execution failed")
            
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        
if __name__ == "__main__":
    main() 