from flask import Flask, request
import csv
from datetime import datetime

app = Flask(__name__)

# Log file path
LOG_FILE = "view_logs.csv"

# Function to log viewer details
def log_view(video_url, client_ip, user_agent):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), video_url, client_ip, user_agent])

@app.route('/track', methods=['GET'])
def track():
    video_url = request.args.get('video_url')
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    # Log the viewer data
    log_view(video_url, client_ip, user_agent)

    # Return a transparent pixel (for pixel tracking)
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\xff\x00\xc0\xc0\xc0\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'
    return pixel, 200, {'Content-Type': 'image/gif'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
