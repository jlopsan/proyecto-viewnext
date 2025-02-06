import { useState } from "react";
import "./ChatInterface.css"; // Importar los estilos externos
import ReactMarkdown from "react-markdown";

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFaq, setShowFaq] = useState(true);
  const [showNewChatButton, setShowNewChatButton] = useState(false);
  const [uuid, setUuid] = useState(null);  // Agregar estado para el UUID

  const handleQuery = async () => {
    if (!question.trim() || isLoading) return;

    setMessages(prev => [...prev, { text: question, isUser: true }]);
    setIsLoading(true);
    setQuestion("");

    setShowFaq(false);
    setShowNewChatButton(true);

    try {
      const requestBody = { pregunta: question };

      // Solo agregar el UUID si existe
      if (uuid) {
        requestBody.uuid = uuid;
      }

      const res = await fetch("http://localhost:8000/agente", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),  // Enviar el cuerpo con pregunta y uuid si existe
      });

      const data = await res.json();
      const cleanedAnswer = data.respuesta ? data.respuesta.replace(/^L3##/i, '').trim() : "No se encontró respuesta.";

      setMessages(prev => [...prev, { text: cleanedAnswer || "No se encontró respuesta.", isUser: false }]);

      try {
        const consulta = {
          "uuid" : data.uuid,
          "consulta": requestBody.pregunta,
          "respuesta": cleanedAnswer,
          "fecha" : new Date()
        };
        const res = await fetch("http://localhost:8000/consulta", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(consulta),  // Enviar el cuerpo con pregunta y uuid para guardarlo en la BD
      });
    } catch (error) {
      console.error("Error al guardar la consulta en la base de datos:", error);
    }
      
      if (!uuid) {
        setUuid(data.uuid);
      }

    } catch (error) {
      console.error("Error al enviar la pregunta:", error);
      setMessages(prev => [...prev, { text: "Error al conectar con el servidor.", isUser: false, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleQuery();
    }
  };

  // Función para iniciar un nuevo chat
  const handleNewChat = () => {
    // Limpiar los campos en el frontend
    setMessages([]); // Limpia los mensajes actuales
    setQuestion(""); // Limpia la pregunta actual
    setUuid(null); // Limpiar el UUID cuando se empieza un nuevo chat
    setShowNewChatButton(false); // Ocultar el botón de nuevo chat
    setShowFaq(true); // Mostrar las preguntas frecuentes
    setIsLoading(false); // Asegurarse de que no haya carga en curso

    console.log('Nuevo chat iniciado: Campos limpiados.');
  };

  return (
    <div className="chat-container">
      <header className="header">
        AsesorIA
        <div className="subtitle">Proyecto ViewNext</div>
      </header>

      <div className="chat-interface">
        {messages.length === 0 && <h1 className="title">¿Cómo puedo ayudarte?</h1>}

        <div className="chat-box">
          <div className="messages-area">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}
              >
                {!message.isUser ? (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                ) : (
                  message.text
                )}
              </div>
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="loading-spinner"></div>
                <span>Generando respuesta...</span>
              </div>
            )}
          </div>

          <div className="input-container">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Envía tu duda al asistente..."
              className="input-field"
              disabled={isLoading}
            />
            <button 
              onClick={handleQuery} 
              className="send-button"
              disabled={isLoading}
            >
              ➤
            </button>
          </div>
        </div>

        {showNewChatButton && (
          <button className="new-chat-button" onClick={handleNewChat}>Nuevo Chat</button>
        )}

        {/* Recuadro de las preguntas frecuentes */}
        {showFaq && (
          <div className="faq-box">
            <h2 className="faq-title">Preguntas Frecuentes</h2>
            <ul className="faq-list">
              <li><strong>¿Cómo puedo acceder a los trámites?</strong></li>
              <li><strong>¿Cuáles son los horarios de atención?</strong></li>
              <li><strong>¿Qué documentos necesito para realizar un trámite?</strong></li>
            </ul>
          </div>
        )}

      </div>
      <footer className="footer"></footer>
    </div>
  );
}
