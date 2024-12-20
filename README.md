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

### Prerequisites
- Python 3.8+
- Google Sheets API credentials
- Access to target spreadsheet

### Quick Start
1. Clone and install dependencies:
```bash
git clone <repository-url>
cd book-genre-classifier
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure:
- Copy `.env.example` to `.env`
- Add your Google Sheets credentials and spreadsheet ID
- Share sheet with service account email

3. Run:
```bash
python main.py
```

## Technical Notes

- Uses Meta's BART model for zero-shot classification
- Confidence threshold: 0.6 (configurable)
- Books below threshold marked as "unknown"
- Results written to adjacent column
- Includes error handling and input validation

## License

MIT License - see LICENSE file