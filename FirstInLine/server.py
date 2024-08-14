import os
import logging
import smtplib
from flask import Flask, request, abort
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build

# Configuration from Environment Variables
API_KEY = os.getenv('API_KEY')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
COMMENT_TEXT = 'YOUR_COMMENT'

# Set up logging with detailed information
logging.basicConfig(
    filename='firstinline_bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

app = Flask(__name__)

def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = RECIPIENT_EMAIL
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def post_comment(video_id, comment_text):
    try:
        youtube.commentThreads().insert(
            part='snippet',
            body={
                'snippet': {
                    'videoId': video_id,
                    'topLevelComment': {
                        'snippet': {
                            'textOriginal': comment_text
                        }
                    }
                }
            }
        ).execute()
        logging.info(f"Comment posted successfully on video {video_id}!")
    except Exception as e:
        logging.error(f"Failed to post comment on video {video_id}: {e}")
        send_email('Error Alert', f'Failed to post comment on video {video_id}: {e}')

def extract_video_id_from_xml(data):
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(data)
        video_id = root.find('.//{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}id').text
        return video_id.split(':')[-1]
    except Exception as e:
        logging.error(f"Error extracting video ID from XML: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.data
        if not data:
            logging.error("No data received in webhook")
            abort(400)

        video_id = extract_video_id_from_xml(data)
        if video_id:
            post_comment(video_id, COMMENT_TEXT)
            send_email(
                'New Comment Posted',
                f'A new comment was posted on video ID: {video_id}\nComment: {COMMENT_TEXT}'
            )
            return 'OK', 200
        else:
            logging.error("Failed to extract video ID")
            abort(400)
    else:
        abort(400)

if __name__ == '__main__':
    # Use SSL if deploying publicly
    app.run(port=5000, ssl_context='adhoc')
