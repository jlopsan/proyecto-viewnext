Para ejecutar el programa adecuadamente es necesario seguir los siguientes pasos:

1º Hay que modificar el archivo .env.example rellenando los parámetros de su interior, TAVILY_API_KEY="Tu_contraseña_de_Tavily", USER_EMAIL= "usuario_para_acceder_a_la_API", API_KEY="contraseña_API", SMTP_SERVER='smtp.gmail.com' que es el servidor que utilizará el LLM para mandar correos, SMTP_PORT=587 puerto autorizado para mandar los correos, SMTP_USER="usuario@gmail.com" el gmail al que se quieran mandar los correos, SMTP_PASSWORD="Contraseña" aquí se pone una de las 10 contraseñas generadas por Google cuando autorizas la autentificación en dos pasos en "Seguridad de la cuenta".

2º Para ejecutar la app primero abrimos el directorio de la carpera frontend en una terminal ejecutamos "npm install" para instalar las dependencias necesarias si no lo hemos ejecutado con anterioridad y después ejecutamos "npm run dev" para iniciar el entorno de desarrollo. La consola nos devuelve la url http donde se está ejecutando el servidor. 

3º En otra terminal diferente ejecutamos "uvicorn main:app --reload" para ejecutar la aplicación web. 
Finalmente ponemos en el buscador la url que nos ha devuelto el programa en el punto 2º y con ello se abrirá nuestra aplicación en local lista para ser usada.