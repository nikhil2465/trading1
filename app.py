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

@app.route('/tools')
def tools():
    return render_template('tools.html')

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
