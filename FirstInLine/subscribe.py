import requests
import os

# Configuration from Environment Variables
API_KEY = os.getenv('API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CALLBACK_URL = os.getenv('CALLBACK_URL')  # Replace with your actual server URL

HUB_URL = 'https://pubsubhubbub.appspot.com/subscribe'
TOPIC_URL = f'https://www.youtube.com/xml/feeds/videos.xml?channel_id={CHANNEL_ID}'

response = requests.post(HUB_URL, data={
    'hub.mode': 'subscribe',
    'hub.topic': TOPIC_URL,
    'hub.callback': CALLBACK_URL,
    'hub.verify': 'async'
})

if response.status_code == 202:
    print('Subscription request accepted')
else:
    print(f'Subscription request failed: {response.status_code}')
