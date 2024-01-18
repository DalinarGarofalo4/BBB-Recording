from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.api.resources.email.html_components import record_ready_email
import os
import smtplib

from app.api.schemas.recording_schema import EmailInput
from app.utils.file_util import (
    format_time, get_metadata_components
)
from app.config import current


async def get_full_folder_path(folder_path: str):
    list_folder_path = list(filter(lambda x: x != '' and x is not None, folder_path.split('/')))
    result: list = []
    for path in list_folder_path:
        if len(result):
            result.append(os.path.join(result[-1], path))
        else:
            result.append(path)
    return result


# TODO: Missing unit tests...
def send_email(email_input: EmailInput):
    sender_email = email_input.sender_email
    to_email = email_input.to_email
    room_name = email_input.room_name
    download_meeting_dir = email_input.download_meeting_dir
    download_link = email_input.download_link
    upload_link = email_input.upload_link
    smtp_server = email_input.smtp_server
    smtp_port = email_input.smtp_port

    # Create a MIME object
    def email_already_sent(directory):
        # Construct the full file path
        file_path = os.path.join(directory, "EMAIL_SENT.txt")

        # Check if the file exists
        return os.path.isfile(file_path)

    if email_already_sent(os.getcwd()):
        print("email was already sent")
    else:
        msg: MIMEMultipart = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "Dirección de descarga de la grabación " + room_name

        metadata_xml_file = os.path.join(
            current.BASE_DIR, current.BBB.DOWNLOADED_MEETINGS_FOLDER, download_meeting_dir, 'metadata.xml'
        )
        time = str(format_time(int(get_metadata_components('start_time', metadata_xml_file))))
        html_content = record_ready_email(time, download_link, upload_link)
        msg.attach(MIMEText(html_content, 'html'))

        # Establish a connection to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.connect(smtp_server, smtp_port)
            # Use TLS for secure connection
            server.starttls()

            # Log in to the email account
            server.login(sender_email, current.EMAIL.SENDER_PASSWORD)

            # Send the email
            server.sendmail(sender_email, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}")
    with open("EMAIL_SENT.txt", 'w') as f:
        f.write("")
