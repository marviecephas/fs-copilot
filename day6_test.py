import os
from twilio.rest import Client

# In Replit, secrets are loaded into os.environ automatically
try:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_whatsapp_number = os.environ["TWILIO_PHONE_NUMBER"]
    to_whatsapp_number = os.environ["MY_PHONE_NUMBER"]
except KeyError as e:
    print(f"❌ Error: Missing Secret {e}. Check your Replit Secrets tab!")
    exit()

# Initialize the Twilio Client
client = Client(account_sid, auth_token)

print(f"Attempting to send message to {to_whatsapp_number}...")

try:
    # Send the message
    message = client.messages.create(
        body="🏎️ FS Co-Pilot: Replit connection successful! I am ready for orders.",
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )
    print(f"✅ Success! Message sent.")
    print(f"SID: {message.sid}")
except Exception as e:
    print(f"❌ Twilio Error: {e}")