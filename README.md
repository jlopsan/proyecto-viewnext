Para ejecutar el programa correctamente, sigue estos pasos:

1. **Configurar el archivo `.env.example`:**
   Abre el archivo `.env.example` y completa los siguientes parámetros con la información correspondiente:
   - `TAVILY_API_KEY="Tu_api_key_de_Tavily"`
   - `USER_EMAIL="usuario_para_acceder_a_la_API"`
   - `API_KEY="contraseña_API"`
   - `SMTP_SERVER="smtp.gmail.com"` (servidor utilizado para enviar correos)
   - `SMTP_PORT=587` (puerto autorizado para enviar correos)
   - `SMTP_USER="usuario@gmail.com"` (el correo de Gmail desde el cual se enviarán los correos)
   - `SMTP_PASSWORD="Contraseña"` (debe ser una contraseña de aplicación cuando habilitas la autenticación en dos pasos en la sección "Seguridad de la cuenta").

2. **Ejecutar el frontend:**
   - Abre una terminal y navega hasta el directorio `frontend`.
   - Ejecuta `npm install` para instalar las dependencias necesarias (si no lo has hecho anteriormente).
   - Luego, ejecuta `npm run dev` para iniciar el entorno de desarrollo. La consola te devolverá la URL en la que el servidor está en ejecución.

3. **Ejecutar el backend:**
   - Abre una terminal diferente y ejecuta `uvicorn main:app --reload` para iniciar la aplicación web.
   - Finalmente, abre el navegador e ingresa la URL proporcionada en el paso 2 para acceder a la aplicación en tu entorno local, lista para ser utilizada.