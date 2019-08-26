import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import datetime

def email(message, subject, email_user, email_password, email_send, files=['none']):

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body,'plain'))

    for filename in files:
        if filename is not 'none':
            attachment = open(filename,'rb')

            part = MIMEBase('application','octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition','attachment; filename= '+filename)

            msg.attach(part)

    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user, email_password)

    server.sendmail(email_user, email_send, text)
    server.quit()

    print('sent message --> '+str(datetime.datetime.now())+'\n---------------------------------------------------------------------\n'+message+'\n\n\n')