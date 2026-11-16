"""Backend de e-mail que envia pela API HTTP do Resend.

O plano gratuito do Render bloqueia as portas de SMTP, então o envio pelo
backend padrão do Django não funciona lá. Este backend usa só a biblioteca
padrão do Python (urllib) e é ativado quando a variável RESEND_API_KEY existe.
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

API_URL = 'https://api.resend.com/emails'


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            payload = {
                'from': message.from_email or settings.DEFAULT_FROM_EMAIL,
                'to': list(message.to),
                'subject': message.subject,
                'text': message.body,
            }
            for content, mimetype in getattr(message, 'alternatives', []):
                if mimetype == 'text/html':
                    payload['html'] = content
            request = urllib.request.Request(
                API_URL,
                data=json.dumps(payload).encode(),
                headers={
                    'Authorization': f'Bearer {settings.RESEND_API_KEY}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'arquivo-kilho/1.0',
                },
                method='POST',
            )
            try:
                with urllib.request.urlopen(request, timeout=15):
                    sent += 1
            except urllib.error.URLError as error:
                logger.error('Falha ao enviar e-mail pelo Resend: %s', error)
                if not self.fail_silently:
                    raise
        return sent
