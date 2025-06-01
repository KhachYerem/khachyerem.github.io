import os.path
import base64
import sys
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("Token Err:", e)
                creds = None
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Ошибка: Не переданы email получателя и/или данные для отправки")
        sys.exit(1)

    to = sys.argv[1] 
    message_text = sys.argv[2] 

    creds = gmail_auth()
    service = build('gmail', 'v1', credentials=creds)

    sender = "khachatryanerems@gmail.com"
    subject = "Результат обработки запроса на проверку запрета въезда"
    message = create_message(sender, to, subject, message_text)
    result = send_message(service, "me", message)
    print("Send. ID:", result['id'])