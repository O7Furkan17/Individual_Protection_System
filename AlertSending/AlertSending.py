import re
import smtplib
import ssl


class AlertSending:

    def __init__(self, smtp_server="smtp.gmail.com", port=465):
        self.smtp_server = smtp_server
        self.port = port
        self.email = ""
        self.password = ""
        self.context = ssl.create_default_context()

    def alertConfig(self, email, password):
        if self.regex_error_checking(email):
            self.email = str(email)
            self.password = str(password)

    def regex_error_checking(self, temp_email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(email_regex, temp_email):
            return True
        else:
            print("Enter a valid e-mail address.")
            return False

    def send_email(self, to_email, subject, body):
        if self.email != "" and self.password != "" and self.regex_error_checking(to_email):
            try:
                with smtplib.SMTP_SSL(self.smtp_server, self.port, context=self.context) as server:
                    server.login(self.email, self.password)
                    message = f"Subject: {subject}\n\n{body}".encode('utf-8')
                    server.sendmail(self.email, to_email, message)
                    print("Email sent successfully!")
            except Exception as e:
                print(f"Email could not be sent: {e}")
        else:
            print("Please enter your email and password first. Method: alertConfig(email,password)")
