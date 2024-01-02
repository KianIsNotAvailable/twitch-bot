import random
import re
import irc
import os
from dotenv import load_dotenv
from clip import download_twitch_clip
from functions import roll_dice
# Load variables from the .env file
load_dotenv()




# Access variables using the os.environ dictionary
BOT_USERNAME = os.getenv("MY_BOT_USERNAME")
OAUTH_TOKEN = os.getenv("MY_OAUTH_TOKEN")
CHANNEL_NAME = os.getenv("MY_CHANNEL_NAME")


# Create a connection to Twitch IRC
client = irc.IRC()
client.connect('irc.twitch.tv', 6667, BOT_USERNAME, OAUTH_TOKEN)

# Join the specified channel
client.join(CHANNEL_NAME)

# Event handler for incoming messages
def on_message(sender, message):
    if sender != BOT_USERNAME:  # Ignore messages from the bot itself
        command_name = message.strip()
        # Check if the message starts with the bot's username
        if message.startswith(f'@{BOT_USERNAME}'):
            # Extract the Twitch clip URL from the message
            clip_url_match = re.search(r'(https?://(?:www\.)?twitch\.tv/\S+/clip/\S+)', message)
            
            if clip_url_match:
                clip_url = clip_url_match.group(1)
                # Extract the clip ID from the URL
                # Split the URL using "/" as the delimiter
                parts = clip_url.split('/')
                # The last part is the clip ID
                clip_id = parts[-1]
                # Split the clip ID using "-" as the delimiter
                clip_id_parts = clip_id.split('-')
                # The last part is the actual clip ID
                actual_clip_id = clip_id_parts[-1]





                
                # Now you can use the clip ID for further processing
                print(f'Found Twitch clip with ID: {actual_clip_id}')
                #function to get the download link
                download_link = download_twitch_clip(actual_clip_id)
                client.send_message(CHANNEL_NAME, f"Click the link below to download the converted video:\n{download_link}")
            else:
                client.send_message(CHANNEL_NAME, 'No valid Twitch clip URL found in the message')
        #Dice command        
        elif command_name == '!dice':
            num = roll_dice()
            client.send_message(CHANNEL_NAME, f'You rolled a {num}')
            print(f'* Executed {command_name} command')
        else:
            print(f'* Unknown command {command_name}')
            


# Set the message event handler
client.on_message = on_message

# Start the bot
client.run()
