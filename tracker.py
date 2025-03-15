from flask import Flask, request, jsonify, send_file, redirect
import csv
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Log file paths
LOG_FILE = "view_logs.csv"
SORTED_LOG_FILE = "sorted_view_logs.csv"

# Initialize CSV file with headers if not present
try:
    with open(LOG_FILE, 'x', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Video URL", "Client IP", "User Agent"])
except FileExistsError:
    pass  # File already exists

# Function to log viewer details
def log_view(video_url, client_ip, user_agent):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), video_url, client_ip, user_agent])

# Track route with redirect feature
@app.route('/track', methods=['GET'])
def track():
    video_url = request.args.get('video_url')
    redirect_url = request.args.get('redirect')
    
    if not video_url or not redirect_url:
        return "❌ Missing 'video_url' or 'redirect' parameter", 400
    
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    # Log the data
    log_view(video_url, client_ip, user_agent)

    # Log for Render console visibility
    print(f"✅ View logged: {video_url} | IP: {client_ip} | User Agent: {user_agent}")

    # Redirect to the original video URL
    return redirect(redirect_url, code=302)

# Route to download sorted logs or full log file
@app.route('/logs', methods=['GET'])
def download_logs():
    log_type = request.args.get('type', 'full')  # Options: 'full' or 'sorted'

    try:
        df = pd.read_csv(LOG_FILE)

        if log_type == 'sorted':
            # Count views per video link
            view_count = df['Video URL'].value_counts().reset_index()
            view_count.columns = ['Video URL', 'View Count']

            # Add total views at the top
            total_views = view_count['View Count'].sum()
            view_count.loc[-1] = ["TOTAL VIEWS", total_views]
            view_count.index = view_count.index + 1
            view_count.sort_index(inplace=True)

            # Save sorted data
            view_count.to_csv(SORTED_LOG_FILE, index=False, encoding='utf-8-sig')
            return send_file(SORTED_LOG_FILE, as_attachment=True)
        else:
            # Download full log file
            return send_file(LOG_FILE, as_attachment=True)

    except Exception as e:
        return f"❌ Error processing log file: {str(e)}"

# Run the app
if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
