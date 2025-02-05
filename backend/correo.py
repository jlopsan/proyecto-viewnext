import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def resumir_consulta(consulta, max_palabras=6):
    """Genera un resumen corto de la consulta."""
    palabras = consulta.split()
    resumen = " ".join(palabras[:max_palabras]) + ("..." if len(palabras) > max_palabras else "")
    return resumen

def enviar_correo(destinatario, consulta, respuesta):
    """Envía un correo con la consulta realizada y la respuesta obtenida."""
    remitente = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    asunto = f"Consulta: {resumir_consulta(consulta)}"

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto

    cuerpo = f"""
    <html>
    <body>
        <h3>Consulta:</h3>
        <p>{consulta}</p>
        <h3>Respuesta:</h3>
        <p>{respuesta}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, "html"))

    try:
        servidor = smtplib.SMTP("smtp-mail.outlook.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        return "Correo enviado correctamente."
    except Exception as e:
        return f"Error al enviar el correo: {e}"
