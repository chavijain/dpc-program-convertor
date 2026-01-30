# Excel Manipulation Web Application

A Python Flask web application that allows you to upload Excel files, manipulate data by removing rows and columns, and generate modified reports.

## Features

- **Upload Excel Files**: Support for `.xlsx` and `.xls` formats
- **Interactive Data Preview**: View your Excel data in a clean, responsive table
- **Row Selection & Removal**: Select multiple rows and remove them with one click
- **Column Removal**: Choose specific columns to remove from your data
- **Real-time Summary**: See live statistics about your data manipulation
- **Reset Functionality**: Revert all changes back to the original data
- **Download Reports**: Export your modified data as a new Excel file

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone or navigate to the project directory:
   ```bash
   cd VS_Project_EXP_sheet
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Upload a File**: Drag and drop an Excel file onto the upload area, or click "Browse Files" to select one.

2. **View Data**: Once uploaded, your data will be displayed in an interactive table with summary statistics.

3. **Remove Rows**: 
   - Check the boxes next to rows you want to remove
   - Click "Remove Selected Rows"

4. **Remove Columns**:
   - Click "Remove Columns" button
   - Select the columns you want to remove in the modal
   - Click "Remove Selected"

5. **Reset Changes**: Click "Reset" to revert all changes back to the original uploaded data.

6. **Download Report**: Click "Download Report" to save your modified data as a new Excel file.

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
├── uploads/              # Temporary file storage (auto-created)
└── README.md
```

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Data Processing**: pandas, openpyxl
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Bootstrap Icons

## License

MIT License
