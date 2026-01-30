# Excel Manipulation Web Application

## Project Overview
A Python Flask web application for Excel file manipulation with features to upload, view, edit, and generate reports from Excel data.

## Tech Stack
- **Backend**: Python Flask with pandas for Excel processing
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Libraries**: pandas, openpyxl for Excel handling

## Project Structure
```
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            
│   └── index.html        # Main UI template
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # Frontend JavaScript
├── uploads/              # Temporary upload storage
└── README.md
```

## Features
- Upload Excel files (.xlsx, .xls)
- Preview Excel data in interactive table
- Select and remove rows/columns
- Generate and download modified reports

## Development
- Run with `python app.py`
- Default port: 5000
- Debug mode enabled for development
