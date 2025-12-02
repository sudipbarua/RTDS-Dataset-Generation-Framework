import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import re

import yaml

sender = 'user4@mydomain.local'
password = 'tuckn2023'
receiver = 'user10@mydomain.local'
subject = "SMTP e-mail test"

# body = """From: From Person <user2@mydomain.local>
# To: To Person <user3@mydomain.local>
#
#
# This is a test e-mail message.
# """
with open("/home/sudip/rtds_project/user_profiles/oop/config.yml") as f:
    data = yaml.safe_load(f)

body = data['emailing']['mailbody'][5]

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender
message["To"] = receiver
message["Subject"] = subject
message["cc"] = 'user7@mydomain.local'
message["Bcc"] = 'user9@mydomain.local'

# Add body to email
message.attach(MIMEText(body, "plain"))

filename = "docs/Nikola_Tesla_and_the_Wireless_Transmission_of_Energy.pdf"  # In same directory as script

# Open PDF file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
filename_filtered = re.split("([^\/]+$)", filename)
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename_filtered[1]}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# try:
#    smtpObj = smtplib.SMTP('10.10.2.186')
#    smtpObj.sendmail(sender, receivers, message)
#    print("Successfully sent email")
#
# except:
#    print("Error: unable to send email")

with smtplib.SMTP('10.10.2.186') as server:
   server.sendmail(sender, receiver, text)
   print("Successfully sent email")
