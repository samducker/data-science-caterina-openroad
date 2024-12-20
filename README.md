# Book Genre Classifier

## Project Context

This project was developed by Caterina Farulla as part of an internship application for Open Road, a digital book publishing company. The task involved analyzing spreadsheet data and showcasing trends in their book catalog.

### Background

Question 6 of the assignment asked to identify and showcase trends in the book data. However, the raw data provided didn't include crucial metadata like descriptions, genres, or fiction/non-fiction classifications. This made trend analysis challenging, particularly for understanding the distribution and evolution of fiction versus non-fiction titles over time.

While the original task data was provided in Excel, I strategically imported it into Google Sheets to leverage the powerful Google Sheets API, enabling automated data processing and updates.

### Solution

This complementary Python project was developed to enhance the data analysis by:
1. Automatically classifying books as fiction or non-fiction using AI
2. Writing the classifications back to the spreadsheet based on the title by utilizing zero-shot classification and an open-source model from Meta (facebook/bart-large-mnli)
3. Enabling trend analysis of fiction vs non-fiction ratios over time

This automated solution demonstrates both technical proficiency and creative problem-solving in working with limited metadata.

## Setup and Usage

### System Requirements
- macOS, Linux, or Windows
- Python 3.9 (recommended) or Python 3.8
- Git

### Prerequisites
1. **Python Installation**:
   - For macOS: `brew install python@3.9`
   - For Linux: `sudo apt-get install python3.9`
   - For Windows: Download from [Python.org](https://www.python.org/downloads/)

2. **Google Sheets Setup**:
   - Google Sheets API credentials (instructions below)
   - Access to target spreadsheet

### Detailed Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd book-genre-classifier
   ```

2. **Set Up Python Virtual Environment**:
   ```bash
   # Create virtual environment
   python3.9 -m venv venv

   # Activate virtual environment
   # For macOS/Linux:
   source venv/bin/activate
   # For Windows:
   .\venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Google Sheets Access**:
   a. Create a Google Cloud Project:
      - Go to [Google Cloud Console](https://console.cloud.google.com/)
      - Create a new project
      - Enable Google Sheets API for your project

   b. Set up credentials:
      - Create a Service Account
      - Download the JSON credentials file
      - Copy `.env.example` to `.env`
      - Add your credentials and spreadsheet ID to `.env`

   c. Share your Google Sheet:
      - Share your spreadsheet with the service account email
      - The email can be found in your JSON credentials file

4. **Verify Installation**:
   ```bash
   # Make sure you're in the virtual environment (you should see (venv) in your prompt)
   # If not, activate it with:
   source venv/bin/activate  # macOS/Linux
   # or
   .\venv\Scripts\activate  # Windows

   # Test the classifier
   python tests/test_classifier.py
   ```

5. **Run the Application**:
   ```bash
   # Make sure you're in the virtual environment
   source venv/bin/activate  # macOS/Linux
   # or
   .\venv\Scripts\activate  # Windows

   python main.py
   ```

### Testing

The project includes a test suite to verify the genre classifier's functionality:

1. **Run the Test Suite**:
   ```bash
   # Activate virtual environment if not already active
   source venv/bin/activate  # macOS/Linux
   # or
   .\venv\Scripts\activate  # Windows

   # Run the test script
   python tests/test_classifier.py
   ```

2. **Test Cases**:
   The test suite includes sample book titles to verify classification:
   - Fiction examples: "The Lord of the Rings", "Pride and Prejudice"
   - Non-fiction examples: "How to Cook Everything", "A Brief History of Time"

### Troubleshooting

1. **Python Version Issues**:
   - If `python3.9` command not found, install Python 3.9 using your system's package manager
   - Alternatively, Python 3.8 will also work

2. **Installation Errors**:
   - Make sure your virtual environment is activated (you should see `(venv)` in your prompt)
   - Try updating pip: `pip install --upgrade pip`
   - If PyTorch installation fails, visit [PyTorch website](https://pytorch.org/) for system-specific instructions

3. **Google Sheets Errors**:
   - Verify your credentials file path in `.env`
   - Ensure the service account has edit access to the spreadsheet
   - Check if the Google Sheets API is enabled in your Google Cloud Console

## Technical Notes

- Uses Meta's BART model for zero-shot classification
- Confidence threshold: 0.6 (configurable)
- Books below threshold marked as "unknown"
- Results written to adjacent column
- Includes error handling and input validation

## License

MIT License - see LICENSE file