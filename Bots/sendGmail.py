import smtplib
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

class gmailObject():
    # Gmail login credentials
    '''Note that the password used here is an application specific password using google's old 
    app password issuing system. It's not through their modern client secrets system.'''
    def __init__(self, usr, pw, sender, receiver, subject, body, files = None):
        self.usr = usr
        self.pw = pw
        self.sender = sender
        self.receiver = receiver
        self.body= body 
        self.subject = subject
        
        # Create the email
        self.msg = MIMEMultipart()
        self.msg['From'] = self.sender
        self.msg['To'] = self.receiver
        self.msg['Subject'] = self.subject
        self.msg.attach(MIMEText(self.body, 'plain'))

        #Attachments
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            self.msg.attach(part)

    '''Sends email  with class attributes'''
    def send (self):
        try:
            # Connect to Gmail's SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(self.usr, self.pw)  # Log in to your Gmail account
            server.sendmail(self.sender, self.receiver, self.msg.as_string())  # Send the email
            server.close()  # Close the connection
            print('Email sent successfully!')
        except Exception as e:
            print(f'Failed to send email. Error: {e}')


# test = gmailObject(os.environ.get('GU'), os.environ.get('GP'), os.environ.get('GU'), os.environ.get('GU'), 'test', 'test complete',files = ['C:\\Users\\shent\\OneDrive\\Desktop\\Coding Stuff\\Python Stuff\\Projects\\Bots\\screenshots\\August 11, 2024 to August 17, 2024.png','C:\\Users\\shent\\OneDrive\\Desktop\\Coding Stuff\\Python Stuff\\Projects\\Bots\\screenshots\\August 18, 2024 to August 24, 2024.png'])
# test.send()