import logging
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(filename='youtube_bot.log', level=logging.INFO)

# API key obtained from the Google Cloud Console
API_KEY = 'YOUR_API_KEY'
# Channel ID of the channel you want to monitor
CHANNEL_ID = 'CHANNEL_ID'

# Email configuration
SENDER_EMAIL = 'your_email@example.com'
RECIPIENT_EMAIL = 'recipient_email@example.com'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_smtp_username'
SMTP_PASSWORD = 'your_smtp_password'

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to handle API errors and log them
def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            logging.error(f"HTTP Error: {e}")
            print("An error occurred. Check the log for details.")
    return wrapper

# Function to check for new video uploads
@handle_error
def check_new_videos():
    # Get the list of videos uploaded to the channel
    response = youtube.search().list(
        channelId=CHANNEL_ID,
        part='snippet',
        order='date',
        type='video',
    ).execute()
    
    # Get the timestamp of the most recent video
    most_recent_video_timestamp = response['items'][0]['snippet']['publishedAt']
    most_recent_video_time = datetime.strptime(most_recent_video_timestamp, '%Y-%m-%dT%H:%M:%SZ')
    
    # Compare the timestamp with the current time
    current_time = datetime.now()
    time_difference = current_time - most_recent_video_time
    
    # If the time difference is small, consider it a new video
    if time_difference.total_seconds() < 300:  # 300 seconds = 5 minutes
        return True
    else:
        return False

# Function to post a comment on the new video
@handle_error
def post_comment(video_id, comment_text):
    # Call the YouTube API to insert a new comment
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
    print("Comment posted successfully!")

# Function to send an email notification
def send_email(subject, body):
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())

if __name__ == '__main__':
    if check_new_videos():
        print("New video detected!")
        # Replace 'VIDEO_ID' and 'YOUR_COMMENT' with appropriate values
        post_comment('VIDEO_ID', 'YOUR_COMMENT')
        send_email('New Comment on Your Video', 'Check your video for a new comment!')
    else:
        print("No new videos.")
