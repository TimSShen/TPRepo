import imaplib, email, os

def readLastGmail(user, password, folder, imap_url='imap.gmail.com', delLast=False):
    '''Returns content of last received email in the given folder as a string. 
    Opens imap connection to gmail with input credentials, selects folder, fetches the last email only. 
    Deleting the email is an option as well after reading.'''
    connection = imaplib.IMAP4_SSL(imap_url)
    try:
        connection.login(user, password)
    except imaplib.IMAP4.error as e:
        print(f'Gmail Read function authentication error: {e}')
    try:
        status, data = connection.select(folder)
        if status == 'OK':
            result, data = connection.uid('search', None, "ALL")
            if result == 'OK':
                #data[0].split()[-1] is the last element in a list of email uids split by spaces.
                lastMsgUID = data[0].split()[-1]
                result, data = connection.uid('fetch', lastMsgUID, '(RFC822)')
                if result == 'OK':
                    email_message = email.message_from_bytes(data[0][1])
                    print('From:' + email_message['From'])
                    print('To:' + email_message['To'])
                    print('Date:' + email_message['Date'])
                    print('Subject:' + str(email_message['Subject']))
                    print('Content:' + str(email_message.get_payload()[:]))
                    content = str(email_message.get_payload()[:])
                    if delLast:
                        print('Deleting read email') 
                        connection.store(lastMsgUID, "+FLAGS", "\\Deleted")
                        connection.expunge()
                    return content

        else:
            print("ERROR: Unable to open mailbox ", status)
    except imaplib.IMAP4.error as e:
        print(f'Gmail Read function error after login: {e}')
    finally: 
        # print('Cleanup')
        connection.close()
        connection.logout() 

# #Test Print
# print(readLastGmail(os.environ.get('GU'),os.environ.get('GP'),'Special',delLast = True))
# print(readLastGmail(os.environ.get('GU'),os.environ.get('GP'),'Special',delLast = True))
