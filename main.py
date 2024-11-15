import os
import requests
import time
import threading
from dotenv import load_dotenv

load_dotenv()

# Setting up session
session = requests.Session()
session.cookies.set('_RoliVerification', os.getenv("A"))

# Configuration from environment variables
url = os.getenv("C")
discord_webhook = os.getenv("D")
player_id = int(os.getenv("B"))

# Payload for the POST request
payload = {
    "player_id": player_id,
    "offer_item_ids": [6512277, 1974973389, 17408283, 2566017817],
    "request_item_ids": [],
    "request_tags": ["upgrade", "any", "downgrade"]
}

def send_to_discord(message):
    """Send a message to the Discord webhook."""
    try:
        data = {"content": message}
        response = requests.post(discord_webhook, json=data)
        if response.status_code not in [200, 204]:
            print(f"Failed to send message to Discord: {response.status_code}")
    except Exception as e:
        print(f"Error sending message to Discord: {e}")

def periodic_discord_update():
    """Send a 'running' message to Discord every hour."""
    while True:
        try:
            send_to_discord("The script is running smoothly!")
            time.sleep(3600)  # Wait for an hour
        except Exception as e:
            print(f"Error in periodic Discord update: {e}")
            time.sleep(60)  # Wait a minute before retrying

# Start the periodic Discord update in a separate thread
thread = threading.Thread(target=periodic_discord_update, daemon=True)
thread.start()

# Main program loop
while True:
    try:
        response = session.post(url, json=payload)
        
        if response.status_code == 201:
            print("Ad created successfully!")
            send_to_discord(f"Ad successfully posted for player {player_id}!")
            time.sleep(1810)  # Wait before retrying
        elif response.status_code == 400 and response.json().get("code") == 7105:
            print("Cooldown has not elapsed, retrying in 5 seconds...")
            time.sleep(5)
        else:
            error_message = f"Unexpected error: {response.status_code}, {response.text}. Restarting program..."
            print(error_message)
            send_to_discord(error_message)
            time.sleep(5)

    except requests.exceptions.ConnectionError:
        print("Connection error occurred. Retrying in 5 seconds...")
        send_to_discord("Connection error occurred. Retrying...")
        time.sleep(5)
