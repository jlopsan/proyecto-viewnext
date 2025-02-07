import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import markdown

def enviar_correo(destinatario, asunto, cuerpo):
    try:
        cuerpo_limpio = cuerpo.replace('L3##', '').strip()

        # Convertir el cuerpo de Markdown a HTML
        cuerpo_html = markdown.markdown(cuerpo_limpio)

        # Obtener configuración del servidor SMTP desde variables de entorno
        servidor_smtp = os.getenv('SMTP_SERVER')
        puerto_smtp = int(os.getenv('SMTP_PORT', 587))
        usuario_smtp = os.getenv('SMTP_USER')
        contraseña_smtp = os.getenv('SMTP_PASSWORD')

        if not all([servidor_smtp, puerto_smtp, usuario_smtp, contraseña_smtp]):
            raise ValueError("Faltan configuraciones de correo en las variables de entorno.")

        # Crear el mensaje con formato alternativo (texto plano y HTML)
        mensaje = MIMEMultipart("alternative")
        mensaje['From'] = formataddr(("AsesorIA", usuario_smtp))
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(cuerpo_limpio, 'plain'))
        mensaje.attach(MIMEText(cuerpo_html, 'html'))

        # Conectar al servidor SMTP y enviar el correo
        with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
            servidor.starttls()
            servidor.login(usuario_smtp, contraseña_smtp)
            servidor.sendmail(usuario_smtp, destinatario, mensaje.as_string())

        return f"El correo fue enviado exitosamente a {destinatario}."
    except Exception as e:
        return f"Error al enviar el correo: {e}"
