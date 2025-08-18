# from flask import Flask, render_template, request
# import pandas as pd
# from data1 import fetch_chartink_scan, scans

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     results_html = None
#     scan_type = None
#     error = None
#     if request.method == 'POST':
#         scan_type = request.form.get('scan_type')
#         clause = scans.get(scan_type)
#         if clause:
#             df = fetch_chartink_scan(clause)
#             if df is not None:
#                 results_html = df.to_html(classes='table table-striped', index=False, escape=False)
#             else:
#                 error = "No data fetched. Check console for errors."
#         else:
#             error = "Invalid scan type."
#     return render_template('index.html', results=results_html, scan_type=scan_type, scans=scans.keys(), error=error)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# working code
# from flask import Flask, render_template, request
# import pandas as pd
# from data1 import fetch_chartink_scan, scans, FALLBACK_DATA

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     results_html = None
#     scan_type = None
#     error = None
#     if request.method == 'POST':
#         scan_type = request.form.get('scan_type')
#         clause = scans.get(scan_type)
#         if clause:
#             df = fetch_chartink_scan(clause)
#             if df is not None:
#                 results_html = df.to_html(classes='table table-striped', index=False, escape=False)
#             else:
#                 # Use fallback if no live data
#                 fallback_df = pd.DataFrame(FALLBACK_DATA)
#                 results_html = fallback_df.to_html(classes='table table-striped', index=False, escape=False)
#         else:
#             error = "Invalid scan type."
#     return render_template('index.html', results=results_html, scan_type=scan_type, scans=scans.keys(), error=error)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# working code
# from flask import Flask, render_template, request
# import pandas as pd
# from data1 import fetch_chartink_scan, scans, FALLBACK_DATA

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     results_html = None
#     scan_type = None
#     error = None

#     if request.method == 'POST':
#         scan_type = request.form.get('scan_type')
#         clause = scans.get(scan_type)
#         if clause:
#             df = fetch_chartink_scan(clause)
#             if df is not None:
#                 # Show live data
#                 results_html = df.to_html(classes='table table-striped', index=False, escape=False)
#             else:
#                 # Use specific fallback data for that scan type
#                 fallback_list = FALLBACK_DATA.get(scan_type, [])
#                 if fallback_list:
#                     fallback_df = pd.DataFrame(fallback_list)
#                     results_html = fallback_df.to_html(classes='table table-striped', index=False, escape=False)
#                 else:
#                     error = "No fallback data available."
#         else:
#             error = "Invalid scan type."

#     return render_template('index.html', results=results_html, scan_type=scan_type, scans=scans.keys(), error=error)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# app.py
# from flask import Flask, render_template, request
# import pandas as pd
# from data1 import fetch_chartink_scan, scans, FALLBACK_DATA

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     results_html = None
#     error = None
#     scan_type = None

#     if request.method == 'POST':
#         scan_type = request.form.get('scan
#         clause = scans.get(scan_type)
#         if clause:
#             df = fetch_chartink_scan(clause)
#             if df is not None:
#                 results_html = df.to_html(classes='table table-striped', index=False, escape=False)
#             else:
#                 fallback_df = pd.DataFrame(FALLBACK_DATA.get(scan_type, []))
#                 results_html = fallback_df.to_html(classes='table table-striped', index=False, escape=False)
#         else:
#             error = "Invalid scan type selected."

#     return render_template('index.html', results=results_html, scan_type=scan_type, scans=scans.keys(), error=error)


# if __name__ == '__main__':
#     app.run(debug=True, port=5000)

from flask import Flask, render_template, request, Response, send_file
import pandas as pd
from data1 import fetch_chartink_scan, scans, FALLBACK_DATA
import os
from werkzeug.utils import secure_filename
from flask import jsonify
import numpy as np

app = Flask(__name__)

# ---------- Main Scanner Page ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    results_html = None
    error = None
    scan_type = None
    current_df = None  # store DataFrame for CSV download
    status = None      # Add status for success messages

    if request.method == 'POST':
        scan_type = request.form.get('scan_type')
        clause = scans.get(scan_type)

        if clause:
            df = fetch_chartink_scan(clause)
            if df is not None and not df.empty:
                current_df = df
                results_html = df.to_html(classes='table table-striped', index=False, escape=False)
                status = "Live data fetched successfully."
            else:
                fallback_df = pd.DataFrame(FALLBACK_DATA.get(scan_type, []))
                current_df = fallback_df
                results_html = fallback_df.to_html(classes='table table-striped', index=False, escape=False)
                status = "Showing fallback data."
            if not results_html:
                results_html = "<p>No results found.</p>"
        else:
            error = "Invalid scan type selected."

    return render_template(
        'index.html',
        results=results_html,
        scan_type=scan_type,
        scans=scans.keys(),
        error=error,
        status=status
    )

# ---------- CSV Download Route ----------
@app.route("/download_csv", methods=['POST'])
def download_csv():
    # Get scan_type from the form to regenerate CSV
    scan_type = request.form.get('scan_type')
    clause = scans.get(scan_type)

    if clause:
        df = fetch_chartink_scan(clause)
        if df is None or df.empty:
            df = pd.DataFrame(FALLBACK_DATA.get(scan_type, []))
    else:
        df = pd.DataFrame()

    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={scan_type}_report.csv"}
    )

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/tools', methods=['GET', 'POST'])
def tools():
    if request.method == 'POST' and 'share_file' in request.files:
        file = request.files['share_file']
        if file.filename != '':
            # Save the uploaded file temporarily
            temp_dir = os.path.join(app.root_path, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename to avoid conflicts
            filename = secure_filename(file.filename)
            upload_path = os.path.join(temp_dir, f"upload_{filename}")
            download_path = os.path.join(temp_dir, f"processed_{filename}")
            
            # Save the uploaded file
            file.save(upload_path)
            
            try:
                # Process the file with the macro
                process_file_with_macro(upload_path, download_path)
                
                # Return the processed file for download
                return send_file(
                    download_path,
                    as_attachment=True,
                    download_name=f"processed_{filename}",
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            except Exception as e:
                # If processing fails, return the original file
                print(f"Error processing file: {str(e)}")
                return send_file(upload_path, as_attachment=True)
    
    # For GET requests or if no file was uploaded
    return render_template('tools.html')

def process_file_with_macro(input_path, output_path):
    """
    Process the Excel file with the macro
    This is a Python implementation of the VBA macro logic from CA_Dayanand_Bongale_Mobile_6362985767
    """
    import pandas as pd
    import numpy as np
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Alignment
    from openpyxl.formatting.rule import ColorScaleRule, FormulaRule
    
    # Read the Excel file
    df = pd.read_excel(input_path)
    
    # 1. Delete specific rows and columns (VBA: Rows("1:1").Delete, Columns("A:A").Delete, etc.)
    # Skip the first row (header)
    if not df.empty:
        df = df.iloc[1:].reset_index(drop=True)
    
    # 2. Format numbers and remove commas
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    
    # 3. Add calculations (PCR OI, PCR Volume, etc.)
    if len(df.columns) >= 7:  # Ensure we have enough columns
        try:
            # PCR OI = Column G / Column A (0-based index 6 / 0)
            df['PCR OI'] = df.iloc[:, 6] / df.iloc[:, 0]
            
            # PCR Volume = Column D / Column B (0-based index 3 / 1)
            df['PCR Volume'] = df.iloc[:, 3] / df.iloc[:, 1]
            
            # PCR Change in OI = Column D / Column C (0-based index 3 / 2)
            df['PCR Change in OI'] = df.iloc[:, 3] / df.iloc[:, 2]
            
            # CPR OI = Column A / Column B (0-based index 0 / 1)
            df['CPR OI'] = df.iloc[:, 0] / df.iloc[:, 1]
            
            # CPR Vol = Column C / Column E (0-based index 2 / 4)
            df['CPR Vol'] = df.iloc[:, 2] / df.iloc[:, 4]
            
            # CPR Sum = CPR OI + CPR Vol
            df['CPR Sum'] = df['CPR OI'] + df['CPR Vol']
            
            # PCR Sum = PCR OI + PCR Volume
            df['PCR Sum'] = df['PCR OI'] + df['PCR Volume']
            
            # Add support levels based on PCR Sum
            conditions = [
                (df['PCR Sum'] > 8),
                (df['PCR Sum'] > 5),
                (df['PCR Sum'] > 3)
            ]
            choices = ['Very Good Support', 'Good Support', 'Support']
            df['PCR Support'] = np.select(conditions, choices, default='')
            
            # Add resistance levels based on CPR Sum
            conditions = [
                (df['CPR Sum'] > 6),
                (df['CPR Sum'] > 3)
            ]
            choices = ['Very Good Resistance', 'Resistance']
            df['Resistance'] = np.select(conditions, choices, default='')
            
        except Exception as e:
            print(f"Error in calculations: {str(e)}")
    
    # Save the processed data to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Processed Data')
        
        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Processed Data']
        
        # Set column widths (similar to VBA's ColumnWidth property)
        column_widths = {
            'A': 15, 'B': 15, 'C': 15, 'D': 15, 'E': 15,
            'F': 15, 'G': 15, 'H': 12, 'I': 12, 'J': 12,
            'K': 12, 'L': 15, 'M': 12, 'N': 12, 'O': 12, 'P': 20
        }
        
        for col_letter, width in column_widths.items():
            worksheet.column_dimensions[col_letter].width = width
        
        # Center align all cells (similar to VBA's HorizontalAlignment)
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add conditional formatting (similar to VBA's FormatConditions)
        # This is a simplified version - Excel's conditional formatting is more powerful
        green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
        
        # Format cells in column H (PCR OI) where value > 1
        for row in range(2, len(df) + 2):  # +2 because Excel is 1-based and we have a header
            cell = worksheet[f'H{row}']
            if cell.value and isinstance(cell.value, (int, float)) and cell.value > 1:
                cell.fill = green_fill
        
        # Format cells in column I (PCR Volume) where value > 1 and not 'ILLIQUID'
        for row in range(2, len(df) + 2):
            cell = worksheet[f'I{row}']
            if (cell.value and 
                isinstance(cell.value, (int, float)) and 
                cell.value > 1 and 
                (not isinstance(worksheet[f'K{row}'].value, str) or 
                 'ILLIQUID' not in str(worksheet[f'K{row}'].value).upper())):
                cell.fill = green_fill
    
    return True

@app.route('/tools_macro_upload', methods=['POST'])
def tools_macro_upload():
    file = request.files.get('excel_file')
    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)
        # Just send back the uploaded file (no macro processing server-side)
        return send_file(temp_path, as_attachment=True)
    return "No file uploaded", 400

@app.route('/tools_paper_trading', methods=['GET', 'POST'])
def tools_paper_trading():
    trade_status = None
    trades_path = os.path.join('c:\\Nikhil imp files\\nikhil_project', 'paper_trades.csv')
    # Load existing trades
    if os.path.exists(trades_path):
        trades_df = pd.read_csv(trades_path)
        trades = trades_df.to_dict('records')
    else:
        trades = []

    if request.method == 'POST':
        symbol = request.form.get('symbol')
        action = request.form.get('action')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        if symbol and action and quantity and price:
            trade_status = f"Paper trade executed: {action.upper()} {quantity} of {symbol.upper()} at {price}"
            new_trade = {'symbol': symbol, 'action': action, 'quantity': quantity, 'price': price}
            trades.append(new_trade)
            # Save trades to CSV
            pd.DataFrame(trades).to_csv(trades_path, index=False)
        else:
            trade_status = "Please fill all fields."
    return render_template('tools_paper_trading.html', trade_status=trade_status, trades=trades)

# The /tools_macro_upload route already supports .txt files as uploaded.
# No changes required unless you want to process TXT data server-side.

################################

# Updated /create_scan route with better column mapping
@app.route('/create_scan', methods=['GET', 'POST'])
def create_scan():
    results_html = None
    error = None
    status = None
    scan_clause = '( {futidx} ( weekly rsi(14) <= 30 and weekly close <= weekly lower bollinger(20,2) ) ) or ( {futidx} ( weekly rsi(14) >= 70 and weekly close >= weekly upper bollinger(20,2) ) )'  # Default from screenshot

    if request.method == 'POST':
        scan_clause = request.form.get('scan_clause', scan_clause)
        df = fetch_chartink_scan(scan_clause)
        if df is not None and not df.empty:
            # Map columns to match Chartink screenshot
            if all(col in df.columns for col in ['nsecode', 'name', 'close', 'per_chg', 'volume']):
                df = df[['nsecode', 'name', 'close', 'per_chg', 'volume']]
                df.columns = ['Symbol', 'Name', 'LTP', '% Chg', 'Volume']
            elif all(col in df.columns for col in ['nsecode', 'name', 'close', 'volume']):
                df['% Chg'] = 0.0  # Default if % Chg not available
                df = df[['nsecode', 'name', 'close', '% Chg', 'volume']]
                df.columns = ['Symbol', 'Name', 'LTP', '% Chg', 'Volume']
            results_html = df.to_html(classes='chartink-table', index=False, escape=False, formatters={'% Chg': '{:.2f}'.format, 'LTP': '{:.2f}'.format, 'Volume': '{:.0f}'.format})
            status = "Live data fetched successfully."
        else:
            fallback_df = pd.DataFrame(FALLBACK_DATA.get('magic_filters', []))
            if not fallback_df.empty:
                fallback_df = fallback_df[['nsecode', 'name', 'close', 'per_chg', 'volume']]
                fallback_df.columns = ['Symbol', 'Name', 'LTP', '% Chg', 'Volume']
                results_html = fallback_df.to_html(classes='chartink-table', index=False, escape=False, formatters={'% Chg': '{:.2f}'.format, 'LTP': '{:.2f}'.format, 'Volume': '{:.0f}'.format})
                status = "Showing fallback data from screenshot."
            else:
                error = "No data available."

    return render_template('create_scan.html', results=results_html, scan_clause=scan_clause, error=error, status=status)

latest_scan_results = []

@app.route('/create_scan/data', methods=['GET', 'POST'])
def create_scan_data():
    global latest_scan_results
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            results = data.get('results', [])
            if not results:
                return 'No data received', 400
            latest_scan_results = results  # Save for GET
            # Render a simple HTML table
            table_html = '<table border="1" cellpadding="5"><tr>'
            if results:
                for col in results[0].keys():
                    table_html += f'<th>{col}</th>'
                table_html += '</tr>'
                for row in results:
                    table_html += '<tr>' + ''.join(f'<td>{row.get(col," ")}</td>' for col in results[0].keys()) + '</tr>'
            table_html += '</table>'
            return f'<h2>Posted Chartink Scan Results</h2>{table_html}'
        return 'Expected JSON POST', 400
    else:  # GET
        results = latest_scan_results
        if not results:
            return '<h2>No scan results posted yet.</h2>'
        table_html = '<table border="1" cellpadding="5"><tr>'
        for col in results[0].keys():
            table_html += f'<th>{col}</th>'
        table_html += '</tr>'
        for row in results:
            table_html += '<tr>' + ''.join(f'<td>{row.get(col," ")}</td>' for col in results[0].keys()) + '</tr>'
        table_html += '</table>'
        return f'<h2>Latest Posted Chartink Scan Results</h2>{table_html}'

@app.route('/tools_pcr_analysis', methods=['GET', 'POST'])
def tools_pcr_analysis():
    if request.method == 'POST':
        if 'pcr_file' not in request.files:
            return 'No file uploaded', 400
            
        file = request.files['pcr_file']
        if file.filename == '':
            return 'No file selected', 400
            
        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            try:
                # Read the Excel file
                df = pd.read_excel(file)
                
                # Process the data (similar to the VBA macro logic)
                # This is a simplified version - you may need to adjust based on your exact requirements
                
                # Example processing (adjust columns as needed):
                if len(df.columns) >= 7:  # Ensure we have enough columns
                    # Add PCR calculations
                    df['PCR OI'] = df.iloc[:, 6] / df.iloc[:, 0]  # Adjust indices based on your data
                    df['PCR Volume'] = df.iloc[:, 3] / df.iloc[:, 1]  # Adjust indices
                    df['PCR Change in OI'] = df.iloc[:, 3] / df.iloc[:, 2]  # Adjust indices
                    
                    # Add CPR calculations
                    df['CPR OI'] = df.iloc[:, 0] / df.iloc[:, 1]  # Adjust indices
                    df['CPR Vol'] = df.iloc[:, 2] / df.iloc[:, 4]  # Adjust indices
                    df['CPR Sum'] = df['CPR OI'] + df['CPR Vol']
                    
                    # Add support/resistance levels
                    df['PCR Sum'] = df['PCR OI'] + df['PCR Volume']
                    
                    # Add support levels
                    conditions = [
                        (df['PCR Sum'] > 8),
                        (df['PCR Sum'] > 5),
                        (df['PCR Sum'] > 3)
                    ]
                    choices = ['Very Good Support', 'Good Support', 'Support']
                    df['PCR Support'] = np.select(conditions, choices, default='')
                    
                    # Add resistance levels
                    conditions = [
                        (df['CPR Sum'] > 6),
                        (df['CPR Sum'] > 3)
                    ]
                    choices = ['Very Good Resistance', 'Resistance']
                    df['Resistance'] = np.select(conditions, choices, default='')
                    
                    # Convert to HTML for display
                    results_html = df.to_html(classes='table table-striped', index=False)
                    return render_template('pcr_analysis.html', results=results_html)
                    
            except Exception as e:
                return f'Error processing file: {str(e)}', 400
                
    return render_template('pcr_analysis.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
