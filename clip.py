import requests
import subprocess
import time

def download_twitch_clip(clip_id):
    # Replace 'your_client_id' and 'your_client_secret' with your actual Twitch API credentials
    client_id = 'your_client_id'
    client_secret = 'your_client_secret'

    # Twitch API endpoint for getting clip information
    api_url = f'https://api.twitch.tv/helix/clips?id={clip_id}'

    # Set up headers with your Twitch API credentials
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {client_secret}',
    }

    # Make a request to the Twitch API
    response = requests.get(api_url, headers=headers)
    clip_info = response.json()

    # Extract video URL from the response
    video_url = clip_info['data'][0]['thumbnail_url'].split('-preview')[0] + '.mp4'

    # Download the video
    video_response = requests.get(video_url)
    timestamp = int(time.time())  # Get the current timestamp
    download_link = f'output_{timestamp}'

    with open(download_link, 'wb') as video_file:
        video_file.write(video_response.content)

    # Convert to MP4 using ffmpeg (assuming it's installed)
    subprocess.run(['ffmpeg', '-i', download_link, f'{download_link}_converted.mp4'])

    # Provide the random download link
    return f"{download_link}_converted.mp4"


