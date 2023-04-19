import csv
import cv2
import datetime
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from tqdm import tqdm

# Replace the filename with the name of your CSV file
filename = 'rtsp.csv'

# Set a timeout value in milliseconds
timeout_ms = 1500

# Initialize counters for up and down streams
up_count = 0
down_count = 0
print(f"\n Check Started")

# Open the log file for writing
with open('stream-down-log.csv', 'w', newline='') as log_file:
    log_writer = csv.writer(log_file)
    log_writer.writerow(['Timestamp', 'Stream Number', 'DVR Name', 'RTSP URL'])
    
    with open(filename, 'r') as csvfile:
        print(f"\n CSV file opened")
        stream_reader = csv.reader(csvfile)
        # Use tqdm to display progress bar
        for row in tqdm(stream_reader):
            number, dvr_name, rtsp_url = row
            # print(f"\n Row {row}")

            # Try to open the RTSP stream using OpenCV with a timeout value
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_POS_MSEC, timeout_ms)

            # Check if the RTSP stream is up
            if not cap.isOpened():
                print(f"Checking stream {number}, {dvr_name}, {rtsp_url} - \033[1;31m Down\033[0m")
                down_count += 1
                # Write the down stream to the log file
                log_writer.writerow([datetime.datetime.now(), number, dvr_name, rtsp_url])
            else:
                print(f"Checking stream {number}, {dvr_name}, {rtsp_url} - Up")
                up_count += 1

            # Release the OpenCV capture object
            cap.release()

# Print summary of up and down streams
print(f"\n{up_count} RTSP streams are up and \033[1;31m{down_count} RTSP streams are down\033[0m")
print(f"\n Check Completed!")

# Send the log file via email
with open('config.json', 'r') as f:
    config = json.load(f)


from_address = config['from_address']
to_address = config['to_address']
subject = config['subject']
body = config['body']
smtp_server = config['smtp_server']
smtp_port = config['smtp_port']
smtp_username = config['smtp_username']
smtp_password = config['smtp_password']

msg = MIMEMultipart()
msg['From'] = from_address
msg['To'] = to_address
msg['Subject'] = subject

msg.attach(MIMEText(body, 'plain'))

with open('stream-down-log.csv', 'rb') as file:
    attachment = MIMEApplication(file.read(), _subtype='csv')
    attachment.add_header('Content-Disposition', 'attachment', filename='stream-down-log.csv')
    msg.attach(attachment)

server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(smtp_username, smtp_password)
server.sendmail(from_address, to_address, msg.as_string())
server.quit()





