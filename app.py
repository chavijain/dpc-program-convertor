from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Email configuration - Update these with your SMTP settings
EMAIL_CONFIG = {
    'smtp_server': 'smtp.office365.com',
    'smtp_port': 587,
    'sender_email': 'chavjain@microsoft.com',  # Your email
    'sender_password': '',  # App password (leave empty to skip auth for testing)
}

# Store uploaded data in memory for manipulation
data_store = {}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_file_flexible(filepath):
    """Try multiple methods to read the file"""
    errors = []
    
    # Method 1: Try openpyxl (for modern .xlsx)
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
        print("Read with openpyxl engine")
        return df
    except Exception as e:
        errors.append(f"openpyxl: {str(e)}")
    
    # Method 2: Try xlrd (for older .xls)
    try:
        df = pd.read_excel(filepath, engine='xlrd')
        print("Read with xlrd engine")
        return df
    except Exception as e:
        errors.append(f"xlrd: {str(e)}")
    
    # Method 3: Try reading as HTML (some Excel exports are HTML)
    try:
        dfs = pd.read_html(filepath)
        if dfs:
            df = dfs[0]
            print("Read as HTML table")
            return df
    except Exception as e:
        errors.append(f"html: {str(e)}")
    
    # Method 4: Try reading as CSV
    try:
        df = pd.read_csv(filepath)
        print("Read as CSV")
        return df
    except Exception as e:
        errors.append(f"csv: {str(e)}")
    
    # Method 5: Try reading as CSV with different delimiters
    for delimiter in ['\t', ';', '|']:
        try:
            df = pd.read_csv(filepath, delimiter=delimiter)
            print(f"Read as CSV with delimiter '{delimiter}'")
            return df
        except Exception:
            pass
    
    raise Exception(f"Could not read file. Tried: {'; '.join(errors)}")


def clean_dataframe_for_json(df):
    """Clean DataFrame to make it JSON serializable"""
    df = df.copy()
    for col in df.columns:
        # Convert datetime columns to string (MM/DD/YYYY format)
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(lambda x: x.strftime('%m/%d/%Y') if pd.notna(x) else '')
        # Convert timedelta columns to string
        elif pd.api.types.is_timedelta64_dtype(df[col]):
            df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else '')
        # Handle other problematic types
        else:
            df[col] = df[col].apply(lambda x: '' if pd.isna(x) else x)
    return df


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            print("Error: No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print("Error: No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        print(f"Received file: {file.filename}")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not filename:
                filename = f"upload_{uuid.uuid4().hex[:8]}.xlsx"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving to: {filepath}")
            file.save(filepath)
            
            try:
                # Read file using flexible method that tries multiple formats
                df = read_file_flexible(filepath)
                
                print(f"Successfully read file with {len(df)} rows and {len(df.columns)} columns")
                
                # Generate unique session ID
                session_id = str(uuid.uuid4())
                
                # Store data for this session
                data_store[session_id] = {
                    'original_df': df.copy(),
                    'current_df': df.copy(),
                    'filename': filename
                }
                
                # Clean DataFrame for JSON serialization (handles NaT, NaN, datetime, etc.)
                clean_df = clean_dataframe_for_json(df)
                
                # Get column names and data preview
                columns = clean_df.columns.tolist()
                # Convert column names to strings in case they are not
                columns = [str(col) for col in columns]
                data = clean_df.head(100).to_dict('records')
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'columns': columns,
                    'data': data,
                    'total_rows': len(df),
                    'total_columns': len(columns)
                })
            except Exception as e:
                print(f"Error reading Excel: {str(e)}")
                return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400
            finally:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        print(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls files'}), 400
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload error: {str(e)}'}), 400


@app.route('/get-data', methods=['POST'])
def get_data():
    """Get current data for a session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    clean_df = clean_dataframe_for_json(df)
    columns = [str(col) for col in clean_df.columns.tolist()]
    records = clean_df.to_dict('records')
    
    return jsonify({
        'columns': columns,
        'data': records,
        'total_rows': len(df),
        'total_columns': len(columns)
    })


@app.route('/remove-rows', methods=['POST'])
def remove_rows():
    """Remove specified rows from the data"""
    data = request.get_json()
    session_id = data.get('session_id')
    row_indices = data.get('row_indices', [])
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # Remove rows by index
    df = df.drop(index=[i for i in row_indices if i in df.index])
    df = df.reset_index(drop=True)
    
    data_store[session_id]['current_df'] = df
    clean_df = clean_dataframe_for_json(df)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df),
        'total_columns': len(df.columns)
    })


@app.route('/remove-columns', methods=['POST'])
def remove_columns():
    """Remove specified columns from the data"""
    data = request.get_json()
    session_id = data.get('session_id')
    column_names = data.get('column_names', [])
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # Remove columns
    df = df.drop(columns=[col for col in column_names if col in df.columns])
    
    data_store[session_id]['current_df'] = df
    clean_df = clean_dataframe_for_json(df)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df),
        'total_columns': len(df.columns)
    })


@app.route('/keep-columns', methods=['POST'])
def keep_columns():
    """Keep only specified columns, remove all others"""
    data = request.get_json()
    session_id = data.get('session_id')
    columns_to_keep = data.get('column_names', [])
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # Find columns that exist in the dataframe (case-insensitive matching)
    df_columns_lower = {str(col).lower().strip(): col for col in df.columns}
    matched_columns = []
    for col in columns_to_keep:
        col_lower = str(col).lower().strip()
        if col_lower in df_columns_lower:
            matched_columns.append(df_columns_lower[col_lower])
        elif col in df.columns:
            matched_columns.append(col)
    
    if not matched_columns:
        return jsonify({'error': 'None of the specified columns were found in the data'}), 400
    
    # Keep only matched columns
    df = df[matched_columns]
    
    # Add duplicate column after ASR with new name
    asr_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'asr':
            asr_col = col
            break
    
    if asr_col is not None:
        # Find position of ASR column and insert new column after it
        asr_idx = df.columns.get_loc(asr_col)
        new_col_name = "Deadline for initial/baseline approved PORs and assets"
        # Create a copy of ASR values for the new column
        new_col_data = df[asr_col].copy()
        # Insert the new column after ASR
        df.insert(asr_idx + 1, new_col_name, new_col_data)
    
    # Add column before DV BB Vol with value 1 month less
    dv_bb_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'dv bb vol':
            dv_bb_col = col
            break
    
    if dv_bb_col is not None:
        # Find position of DV BB Vol column and insert new column before it
        dv_idx = df.columns.get_loc(dv_bb_col)
        new_col_name2 = "Deadline for final approved PORs and assets; any changes from ASR baseline requires DCR and CRB"
        # Create values that are 1 month less than DV BB Vol
        def subtract_one_month(val):
            if pd.isna(val):
                return val
            try:
                if isinstance(val, pd.Timestamp):
                    # Subtract 1 month
                    return val - pd.DateOffset(months=1)
                elif isinstance(val, str):
                    # Try to parse as date
                    parsed = pd.to_datetime(val, errors='coerce')
                    if pd.notna(parsed):
                        return parsed - pd.DateOffset(months=1)
                return val
            except:
                return val
        
        new_col_data2 = df[dv_bb_col].apply(subtract_one_month)
        # Insert the new column before DV BB Vol
        df.insert(dv_idx, new_col_name2, new_col_data2)
    
    data_store[session_id]['current_df'] = df
    clean_df = clean_dataframe_for_json(df)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns_kept': len(matched_columns)
    })


@app.route('/reset-data', methods=['POST'])
def reset_data():
    """Reset data to original state"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    # Reset to original
    data_store[session_id]['current_df'] = data_store[session_id]['original_df'].copy()
    df = data_store[session_id]['current_df']
    clean_df = clean_dataframe_for_json(df)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df),
        'total_columns': len(df.columns)
    })


@app.route('/transpose', methods=['POST'])
def transpose_data():
    """Transpose the data (swap rows and columns)"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # First convert datetime columns to MM/DD/YYYY format before transposing
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if pd.api.types.is_datetime64_any_dtype(df_formatted[col]):
            df_formatted[col] = df_formatted[col].apply(lambda x: x.strftime('%m/%d/%Y') if pd.notna(x) else '')
    
    # Transpose the dataframe
    df_transposed = df_formatted.T
    
    # Reset index to make it a column and reset column names
    df_transposed = df_transposed.reset_index()
    df_transposed.columns = ['Field'] + [f'Row {i+1}' for i in range(len(df_transposed.columns) - 1)]
    
    data_store[session_id]['current_df'] = df_transposed
    clean_df = clean_dataframe_for_json(df_transposed)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df_transposed),
        'total_columns': len(df_transposed.columns)
    })


@app.route('/transpose-split', methods=['POST'])
def transpose_split_data():
    """Transpose the Spring 2026 and Fall 2026 data separately"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # Find the Program column
    program_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'program':
            program_col = col
            break
    
    spring_programs = ['Woodhaven', 'Marietta', 'San Clemente', 'Rosemont', 'Pullenvale']
    fall_programs = ['Minos', 'Misawa', 'Fernvale']
    
    def transpose_df(df_subset, program_names):
        """Helper function to transpose a dataframe and use program names as column headers"""
        if df_subset.empty:
            return pd.DataFrame()
        
        # Convert datetime columns to MM/DD/YYYY format
        df_formatted = df_subset.copy()
        for col in df_formatted.columns:
            if pd.api.types.is_datetime64_any_dtype(df_formatted[col]):
                df_formatted[col] = df_formatted[col].apply(lambda x: x.strftime('%m/%d/%Y') if pd.notna(x) else '')
        
        # Get program names from the data for column headers
        if program_col and program_col in df_formatted.columns:
            col_names = df_formatted[program_col].astype(str).tolist()
        else:
            col_names = [f'Program {i+1}' for i in range(len(df_formatted))]
        
        # Transpose
        df_transposed = df_formatted.T
        df_transposed = df_transposed.reset_index()
        df_transposed.columns = ['Field'] + col_names
        
        return df_transposed
    
    if program_col:
        spring_df = df[df[program_col].astype(str).str.strip().isin(spring_programs)].reset_index(drop=True)
        fall_df = df[df[program_col].astype(str).str.strip().isin(fall_programs)].reset_index(drop=True)
        
        spring_transposed = transpose_df(spring_df, spring_programs)
        fall_transposed = transpose_df(fall_df, fall_programs)
        
        clean_spring = clean_dataframe_for_json(spring_transposed)
        clean_fall = clean_dataframe_for_json(fall_transposed)
    else:
        clean_spring = pd.DataFrame()
        clean_fall = pd.DataFrame()
    
    return jsonify({
        'success': True,
        'spring_2026': {
            'columns': [str(col) for col in clean_spring.columns.tolist()] if not clean_spring.empty else [],
            'data': clean_spring.to_dict('records') if not clean_spring.empty else [],
            'total_rows': len(clean_spring)
        },
        'fall_2026': {
            'columns': [str(col) for col in clean_fall.columns.tolist()] if not clean_fall.empty else [],
            'data': clean_fall.to_dict('records') if not clean_fall.empty else [],
            'total_rows': len(clean_fall)
        }
    })


@app.route('/filter-rows', methods=['POST'])
def filter_rows():
    """Keep only rows where a column matches specified values"""
    data = request.get_json()
    session_id = data.get('session_id')
    column_name = data.get('column_name')
    filter_values = data.get('filter_values', [])
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    if column_name not in df.columns:
        return jsonify({'error': f'Column "{column_name}" not found'}), 400
    
    # Filter rows where the column value is in the filter_values list
    # Convert to string for comparison to handle mixed types
    df_filtered = df[df[column_name].astype(str).str.strip().isin([str(v).strip() for v in filter_values])]
    
    # Sort rows by the specified filter values order
    filter_order = {str(v).strip(): i for i, v in enumerate(filter_values)}
    df_filtered['_sort_order'] = df_filtered[column_name].astype(str).str.strip().map(filter_order)
    df_filtered = df_filtered.sort_values('_sort_order').drop(columns=['_sort_order'])
    df_filtered = df_filtered.reset_index(drop=True)
    
    data_store[session_id]['current_df'] = df_filtered
    clean_df = clean_dataframe_for_json(df_filtered)
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df_filtered),
        'total_columns': len(df_filtered.columns),
        'rows_kept': len(df_filtered),
        'rows_removed': len(df) - len(df_filtered)
    })


@app.route('/quick-process', methods=['POST'])
def quick_process():
    """Process the data in one click - filter rows, keep columns, add calculated columns"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    
    # Step 1: Filter rows by Program names
    program_names = ['Woodhaven', 'Marietta', 'San Clemente', 'Rosemont', 'Pullenvale', 'Minos', 'Misawa', 'Fernvale']
    
    # Find the Program column (case-insensitive)
    program_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'program':
            program_col = col
            break
    
    if program_col:
        df = df[df[program_col].astype(str).str.strip().isin(program_names)]
        # Sort rows by the specified program order
        program_order = {name: i for i, name in enumerate(program_names)}
        df['_sort_order'] = df[program_col].astype(str).str.strip().map(program_order)
        df = df.sort_values('_sort_order').drop(columns=['_sort_order'])
        df = df.reset_index(drop=True)
    
    # Step 2: Keep only specified columns
    columns_to_keep = ['Program', 'BCR', 'BOP', 'ASR', 'EV1 BB Vol', 'DCR and CRB', 'EV2 BB Vol', 
                       'EMV', 'DV BB Vol', 'DVR', 'Mfg Build  Start', 'SW - PQBIH', 'PQ_RTM', 
                       'SW - RTM', 'PQS', 'SW - RTP BIH', 'Ready to Sell']
    
    df_columns_lower = {str(col).lower().strip(): col for col in df.columns}
    matched_columns = []
    for col in columns_to_keep:
        col_lower = str(col).lower().strip()
        if col_lower in df_columns_lower:
            matched_columns.append(df_columns_lower[col_lower])
        elif col in df.columns:
            matched_columns.append(col)
    
    if matched_columns:
        df = df[matched_columns]
    
    # Step 3: Add column after ASR
    asr_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'asr':
            asr_col = col
            break
    
    if asr_col is not None:
        asr_idx = df.columns.get_loc(asr_col)
        new_col_name = "Deadline for initial/baseline approved PORs and assets"
        new_col_data = df[asr_col].copy()
        df.insert(asr_idx + 1, new_col_name, new_col_data)
    
    # Step 4: Add column before DV BB Vol (1 month less)
    dv_bb_col = None
    for col in df.columns:
        if str(col).lower().strip() == 'dv bb vol':
            dv_bb_col = col
            break
    
    if dv_bb_col is not None:
        dv_idx = df.columns.get_loc(dv_bb_col)
        new_col_name2 = "Deadline for final approved PORs and assets; any changes from ASR baseline requires DCR and CRB"
        
        def subtract_one_month(val):
            if pd.isna(val):
                return val
            try:
                if isinstance(val, pd.Timestamp):
                    return val - pd.DateOffset(months=1)
                elif isinstance(val, str):
                    parsed = pd.to_datetime(val, errors='coerce')
                    if pd.notna(parsed):
                        return parsed - pd.DateOffset(months=1)
                return val
            except:
                return val
        
        new_col_data2 = df[dv_bb_col].apply(subtract_one_month)
        df.insert(dv_idx, new_col_name2, new_col_data2)
    
    data_store[session_id]['current_df'] = df
    clean_df = clean_dataframe_for_json(df)
    
    # Split data into Spring 2026 and Fall 2026
    spring_programs = ['Woodhaven', 'Marietta', 'San Clemente', 'Rosemont', 'Pullenvale']
    fall_programs = ['Minos', 'Misawa', 'Fernvale']
    
    if program_col:
        spring_df = df[df[program_col].astype(str).str.strip().isin(spring_programs)].reset_index(drop=True)
        fall_df = df[df[program_col].astype(str).str.strip().isin(fall_programs)].reset_index(drop=True)
        
        clean_spring_df = clean_dataframe_for_json(spring_df)
        clean_fall_df = clean_dataframe_for_json(fall_df)
    else:
        clean_spring_df = clean_df
        clean_fall_df = pd.DataFrame()
    
    return jsonify({
        'success': True,
        'columns': [str(col) for col in clean_df.columns.tolist()],
        'data': clean_df.to_dict('records'),
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'split_view': True,
        'spring_2026': {
            'columns': [str(col) for col in clean_spring_df.columns.tolist()],
            'data': clean_spring_df.to_dict('records'),
            'total_rows': len(clean_spring_df)
        },
        'fall_2026': {
            'columns': [str(col) for col in clean_fall_df.columns.tolist()],
            'data': clean_fall_df.to_dict('records'),
            'total_rows': len(clean_fall_df)
        }
    })


@app.route('/download-report', methods=['POST'])
def download_report():
    """Generate and download the modified Excel report"""
    data = request.get_json()
    session_id = data.get('session_id')
    split_view = data.get('split_view', False)
    transposed = data.get('transposed', False)
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    original_filename = data_store[session_id]['filename']
    
    # Generate output filename
    name, ext = os.path.splitext(original_filename)
    output_filename = f"{name}_modified.xlsx"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    def transpose_df_for_download(df_subset, program_col):
        """Helper function to transpose a dataframe for download"""
        if df_subset.empty:
            return df_subset
        
        # Convert datetime columns to MM/DD/YYYY format
        df_formatted = df_subset.copy()
        for col in df_formatted.columns:
            if pd.api.types.is_datetime64_any_dtype(df_formatted[col]):
                df_formatted[col] = df_formatted[col].apply(lambda x: x.strftime('%m/%d/%Y') if pd.notna(x) else '')
        
        # Get program names from the data for column headers
        if program_col and program_col in df_formatted.columns:
            col_names = df_formatted[program_col].astype(str).tolist()
        else:
            col_names = [f'Program {i+1}' for i in range(len(df_formatted))]
        
        # Transpose
        df_transposed = df_formatted.T
        df_transposed = df_transposed.reset_index()
        df_transposed.columns = ['Field'] + col_names
        
        return df_transposed
    
    if split_view:
        # Find the Program column
        program_col = None
        for col in df.columns:
            if str(col).lower().strip() == 'program':
                program_col = col
                break
        
        spring_programs = ['Woodhaven', 'Marietta', 'San Clemente', 'Rosemont', 'Pullenvale']
        fall_programs = ['Minos', 'Misawa', 'Fernvale']
        
        if program_col:
            spring_df = df[df[program_col].astype(str).str.strip().isin(spring_programs)].reset_index(drop=True)
            fall_df = df[df[program_col].astype(str).str.strip().isin(fall_programs)].reset_index(drop=True)
            
            # Transpose if needed
            if transposed:
                spring_df = transpose_df_for_download(spring_df, program_col)
                fall_df = transpose_df_for_download(fall_df, program_col)
            
            # Save to Excel with two sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                spring_df.to_excel(writer, sheet_name='Spring 2026', index=False)
                fall_df.to_excel(writer, sheet_name='Fall 2026', index=False)
        else:
            df.to_excel(output_path, index=False)
    else:
        # Save to Excel (single sheet)
        df.to_excel(output_path, index=False)
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/get-summary', methods=['POST'])
def get_summary():
    """Get summary statistics of the current data"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    original_df = data_store[session_id]['original_df']
    
    summary = {
        'original_rows': len(original_df),
        'original_columns': len(original_df.columns),
        'current_rows': len(df),
        'current_columns': len(df.columns),
        'rows_removed': len(original_df) - len(df),
        'columns_removed': len(original_df.columns) - len(df.columns)
    }
    
    return jsonify(summary)


@app.route('/email-report', methods=['POST'])
def email_report():
    """Generate and email the modified Excel report"""
    data = request.get_json()
    session_id = data.get('session_id')
    recipient_email = data.get('email', 'chavjain@microsoft.com')
    
    if session_id not in data_store:
        return jsonify({'error': 'Session not found'}), 404
    
    df = data_store[session_id]['current_df']
    original_filename = data_store[session_id]['filename']
    
    # Generate output filename
    name, ext = os.path.splitext(original_filename)
    output_filename = f"{name}_modified.xlsx"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Save to Excel
    df.to_excel(output_path, index=False)
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = f'DPC Report: {output_filename}'
        
        # Email body
        body = f"""Hi,

Please find attached the processed DPC report.

File: {output_filename}
Rows: {len(df)}
Columns: {len(df.columns)}

This report was generated by the Data from DPC convertor tool.

Best regards,
DPC Convertor Tool
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the Excel file
        with open(output_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {output_filename}')
            msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        
        # Only authenticate if password is provided
        if EMAIL_CONFIG['sender_password']:
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        
        server.sendmail(EMAIL_CONFIG['sender_email'], recipient_email, msg.as_string())
        server.quit()
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return jsonify({
            'success': True,
            'message': f'Report sent successfully to {recipient_email}'
        })
        
    except Exception as e:
        print(f"Email error: {str(e)}")
        return jsonify({
            'error': f'Failed to send email: {str(e)}. You may need to configure SMTP credentials.'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
