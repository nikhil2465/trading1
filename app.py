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
from flask import Flask, render_template, request
import pandas as pd
from data1 import fetch_chartink_scan, scans, FALLBACK_DATA

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results_html = None
    error = None
    scan_type = None

    if request.method == 'POST':
        scan_type = request.form.get('scan_type')
        clause = scans.get(scan_type)
        if clause:
            df = fetch_chartink_scan(clause)
            if df is not None:
                results_html = df.to_html(classes='table table-striped', index=False, escape=False)
            else:
                fallback_df = pd.DataFrame(FALLBACK_DATA.get(scan_type, []))
                results_html = fallback_df.to_html(classes='table table-striped', index=False, escape=False)
        else:
            error = "Invalid scan type selected."

    return render_template('index.html', results=results_html, scan_type=scan_type, scans=scans.keys(), error=error)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
