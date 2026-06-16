import os
import requests
from dotenv import load_dotenv

load_dotenv()

short_token = input("Enter your short-lived Facebook access token: ")
client_id = os.environ["FACEBOOK_APP_ID"]
client_secret = os.environ["FACEBOOK_APP_SECRET"]

facebook_api_url = f"https://graph.facebook.com/v25.0/oauth/access_token?grant_type=fb_exchange_token&client_id={client_id}&client_secret={client_secret}&fb_exchange_token="

r = requests.get(facebook_api_url + short_token)

short_token = r.json().get("access_token")
print("Received 60d token: " + short_token)

r = requests.get(facebook_api_url + short_token)
long_token = r.json().get("access_token")

print("\n\nReceived permanent token: " + long_token)