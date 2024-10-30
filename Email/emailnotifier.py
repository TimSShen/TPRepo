import sys
import os.path
import base64
# import json
# import re
# import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from notify_run import Notify 
# import logging
'''Uses notify.run, a public server that receives messages from this script and sends it via chrome notification 
to a subscribed android phone from the site using a QR code. Messages can be intercepted at the server so it is not secure.'''
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']
notify = Notify() 

def readEmails():
    '''This generates credentials from a client secrets file downloaded from the Gcloud platform associated with my google account. That secrets file is not part of public repo.
    Uses those credentials to request a service object that allow API calls to the gmail API.
    Finds all unread emails that are from the email address of interest and finds the search words in them. Returns true if any email contains all the search words.
    CAVEAT: Google revokes its token refresh access every 7 days if the program is denoted as in "test". Must put in production if token is to work continually.
    '''
    '''Initial Global Variables
    searchPhrases = Phrases we are trying to find in the email to send us a notification about
    wordsFound = Variable that is returned to notify us if any messages contained the search words or not.
    fromEmail = email source that we are scanning for emails from
    tokenPath = Path where token.json is found (or to be saved)
    '''
    searchPhrases=['registration will OPEN', 'registration opens']
    fromEmail = 'earlyon@lumenus.ca'
    tokenPath = 'C:\\Users\\shent\\OneDrive\\Desktop\\Coding Stuff\\Python Stuff\\Projects\\Email\\credentials\\token.json'
    credPath = 'C:\\Users\\shent\\OneDrive\\Desktop\\Coding Stuff\\Python Stuff\\Projects\\Email\\credentials\\credentials.json'                            
    wordsFound = 0
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        if os.path.exists(tokenPath):
            creds =  Credentials.from_authorized_user_file(tokenPath, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(               
                    # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                    credPath, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(tokenPath, 'w') as token:
                token.write(creds.to_json())
    except Exception as error:
        print(f'A credentials error occurred: {error}')
        notify.send('Email Notifier broke: Credentials') 
    
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q= f'is:unread category:primary from:{fromEmail}', maxResults = 10).execute()
        messages = results.get('messages',[])
        if not messages:
            print('No new messages.')
        else:
            message_count = 0
            messageTotal = len(messages)
            print(f'There is {messageTotal} messages')
            for message in messages:
                message_count +=1
                msg = service.users().messages().get(userId='me', id=message['id']).execute() 
                email_headers = msg['payload']['headers']
                for values in email_headers:
                    name = values['name']
                    if name == 'Subject':
                        from_name= values['value']   
                print(f'{message_count}: {from_name}')
                for part in msg['payload']['parts']:
                    try:
                        data = part['body']["data"]
                        byte_code = base64.urlsafe_b64decode(data)
                        text = byte_code.decode("utf-8")
                        wordsFound = False
                        for words in searchPhrases:
                            if text.find(words) >0:
                                wordsFound +=1
                   
                    except BaseException as error:
                        print(f'A message data decode/search error occurred: {error}')
                        notify.send('Email Notifier broke: Message Processing')
                          #mark the message as read (optional)
                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ["UNREAD"]}).execute()                                             
            return wordsFound

    except Exception as error:
        print(f'A google API error occurred: {error}')
        notify.send('Email Notifier broke: Google API call') 

if readEmails() == True:
    notify.send('Lumenus sent an email about a registration date')
else:
    # notify.send('No registration email today')
    print('No registration emails detected')

