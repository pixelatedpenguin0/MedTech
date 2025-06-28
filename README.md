# MedTech - Medication Reminder Web App

A web-based application that helps users manage their medications, set reminders, and track adherence.

## Features

- User authentication and account management
- Medication management (add, edit, delete)
- OCR-based prescription label scanning
- Drug information retrieval from openFDA API
- Medication reminders with browser notifications
- Adherence tracking and visualization
- Responsive design for mobile and desktop

## Tech Stack

- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Backend**: Python (Flask)
- **Database**: SQLite
- **APIs**: openFDA Drug Labeling API, RxNorm API
- **OCR**: Tesseract OCR
- **Notifications**: Browser Notifications API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medtech.git
cd medtech
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
OPENFDA_API_KEY=your-openfda-api-key
RXNORM_API_KEY=your-rxnorm-api-key
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`.

## Usage

1. Register a new account or login with existing credentials.
2. Add medications manually or scan prescription labels.
3. Set up reminders for each medication.
4. Track medication adherence.
5. View adherence history and statistics.

## API Integration

### openFDA API
The application uses the openFDA Drug Labeling API to retrieve medication information. You need to register for an API key at [openFDA](https://open.fda.gov/apis/authentication/).

### RxNorm API
For standardized medication names and identifiers, the application uses the RxNorm API. No API key is required for basic usage.

## OCR Functionality

The application uses Tesseract OCR to extract text from prescription labels. Make sure Tesseract is installed on your system:

- **Windows**: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [openFDA](https://open.fda.gov/) for the drug labeling API
- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/) for medication standardization
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Chart.js](https://www.chartjs.org/) for data visualization 
