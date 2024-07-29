import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend
import os

class CustomEmailBackend(EmailBackend):
    def open(self):
        """Ensure we have an open connection."""
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP(self.host, self.port)
            self.connection.ehlo()
            # Get the absolute path to cacert.pem
            cacert_path = os.path.join(os.path.dirname(__file__), '..', 'certs', 'cacert.pem')
            context = ssl.create_default_context(cafile=cacert_path)
            self.connection.starttls(context=context)
            self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
        except:
            if not self.fail_silently:
                raise
        return True
