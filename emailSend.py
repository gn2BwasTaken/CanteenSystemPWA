from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

isAllowingEmailStuff = False #sir you can make this true to check out the email sending system, just be warned it does require you to log in if you do it.

if isAllowingEmailStuff:
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Authenticate
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    sent_message = service.users().messages().send(userId=user_id, body=message).execute()
    print(f"Message sent! ID: {sent_message['id']}")
    return sent_message

def send_basic_message(mailAddress, subject, body):
    if isAllowingEmailStuff:
        message = create_message("",mailAddress,subject,body)
        send_message(service,"me",message)


'''
sender = "your_email@gmail.com"
to = "shadowgod266@outlook.com"
subject = "Hello from Gmail API"
body = "This is a test email sent using the Gmail API and Python!"

message = create_message(sender, to, subject, body)
send_message(service, "me", message)
'''