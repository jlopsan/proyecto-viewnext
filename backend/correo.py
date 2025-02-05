import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

def enviar_correo(destinatario, consulta, respuesta):
    """Envía un correo con la consulta realizada y la respuesta obtenida."""
    remitente = os.getenv("EMAIL_USER") 
    password = os.getenv("EMAIL_PASSWORD")

    if not remitente or not password:
        return "Error: Las credenciales de correo no están configuradas."

    asunto = f"Consulta: {consulta[:50]}..."  

    # Crear el mensaje
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
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        return "Correo enviado correctamente."
    except smtplib.SMTPAuthenticationError as e:
        return f"Error de autenticación: {e}"
    except smtplib.SMTPException as e:
        return f"Error al enviar el correo: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"

# if __name__ == "__main__":
#     destinatario = "raulcasta_23@hotmail.com"
#     consulta = "Requisitos para obtener una beca en estudios de FP"
#     respuesta = "Los requisitos incluyen estar matriculado en un ciclo formativo y cumplir con los umbrales de renta."

#     resultado = enviar_correo(destinatario, consulta, respuesta)
#     print(resultado)
