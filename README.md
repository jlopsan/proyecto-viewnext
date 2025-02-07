## Instrucciones de ejecución

Para ejecutar el programa correctamente, sigue estos pasos:

1. **Configura el archivo `.env.example`**: Rellena los parámetros dentro del archivo `.env.example` con tus propios valores:
   - `TAVILY_API_KEY="Tu_contraseña_de_Tavily"`
   - `USER_EMAIL="usuario_para_acceder_a_la_API"`
   - `API_KEY="contraseña_API"`
   - `SMTP_SERVER="smtp.gmail.com"` (servidor utilizado para enviar correos)
   - `SMTP_PORT=587` (puerto autorizado para el envío de correos)
   - `SMTP_USER="usuario@gmail.com"` (correo electrónico desde el que se enviarán los correos)
   - `SMTP_PASSWORD="Contraseña"` (una de las contraseñas generadas por Google al habilitar la autenticación en dos pasos en "Seguridad de la cuenta").

2. **Inicia el entorno de desarrollo**:
   - Abre una terminal en el directorio `frontend` y ejecuta:
     ```bash
     npm install
     ```
     para instalar las dependencias necesarias si aún no lo has hecho.
   - Luego, ejecuta:
     ```bash
     npm run dev
     ```
     para iniciar el entorno de desarrollo. La consola mostrará la URL donde se está ejecutando el servidor.

3. **Ejecuta la aplicación web**:
   - Abre otra terminal y ejecuta el siguiente comando:
     ```bash
     uvicorn main:app --reload
     ```
   - Una vez que el servidor esté en ejecución, abre un navegador y pon la URL proporcionada en el paso 2 para acceder a la aplicación localmente.
