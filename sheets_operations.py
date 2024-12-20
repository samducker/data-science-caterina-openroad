"""Module for handling Google Sheets operations."""

from typing import List, Tuple, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials as ServiceAccountCreds

def get_service(credentials_path: str) -> Optional[build]:
    """
    Create and return a Google Sheets service object.
    
    Args:
        credentials_path: Path to the service account credentials JSON file
        
    Returns:
        Google Sheets service object or None if creation fails
    """
    try:
        credentials = ServiceAccountCreds.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        print(f"Failed to create sheets service: {str(e)}")
        return None

def read_book_titles(
    service: build,
    spreadsheet_id: str,
    range_name: str
) -> List[Tuple[str, int, str]]:
    """
    Read book titles from specified Google Sheet.
    
    Args:
        service: Google Sheets service object
        spreadsheet_id: ID of the target spreadsheet
        range_name: A1 notation of the range to read
        
    Returns:
        List of tuples containing (book_title, row_number, column_letter)
    """
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        # Extract the column letter and starting row from the range
        # e.g., 'Sheet1!E2:E' -> column='E', start_row=2
        range_parts = range_name.split('!')
        cell_range = range_parts[1].split(':')[0]
        column = ''.join(c for c in cell_range if c.isalpha())
        start_row = int(''.join(c for c in cell_range if c.isdigit()) or '1')
            
        # Process data with correct row numbers
        return [
            (row[0], start_row + idx, column)  # Row number starts from the specified start row
            for idx, row in enumerate(values)
            if row  # Skip empty rows
        ]
    except HttpError as e:
        print(f"Error reading from Google Sheets: {str(e)}")
        return []

def write_genres(
    service: build,
    spreadsheet_id: str,
    updates: List[Tuple[str, str]]  # (cell_range, genre)
) -> bool:
    """
    Write genre classifications back to the Google Sheet.
    
    Args:
        service: Google Sheets service object
        spreadsheet_id: ID of the target spreadsheet
        updates: List of tuples containing cell ranges and corresponding genres
        
    Returns:
        Boolean indicating success of the operation
    """
    try:
        batch_data = {
            'valueInputOption': 'RAW',
            'data': [
                {
                    'range': cell_range,
                    'values': [[genre]]
                }
                for cell_range, genre in updates
            ]
        }
        
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_data
        ).execute()
        return True
        
    except HttpError as e:
        print(f"Error writing to Google Sheets: {str(e)}")
        return False 