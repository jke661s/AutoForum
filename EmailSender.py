import smtplib
from email.mime.text import MIMEText
from email.header import Header


class EmailSender:
    def __init__(self,
                 username="jke661s.robot@gmail.com",
                 password="pmguoqzrttjifnlu"):
        self.username = username
        self.password = password

    def send_email(self, subject, content):
        sender = self.username
        receivers = ["jacky0105wang@gmail.com", "jessieeeewang@gmail.com"]
        # receivers = ["jacky0105wang@gmail.com"]

        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = Header("ForumAutomator", 'utf-8')
        message['To'] = Header(",".join(receivers), 'utf-8')

        message['Subject'] = Header(subject, 'utf-8')
        try:
            # Create your SMTP session
            smtp = smtplib.SMTP('smtp.gmail.com', 587)

            # Use TLS to add security
            smtp.starttls()

            # User Authentication
            smtp.login(self.username, self.password)

            # Sending the Email
            smtp.sendmail(sender, receivers, message.as_string())

            # Terminating the session
            smtp.quit()
            print("Email sent successfully!")

        except Exception as ex:
            print("Something went wrong....", ex)
