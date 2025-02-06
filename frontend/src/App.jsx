import { useState } from "react";
import "./ChatInterface.css"; // Importar los estilos externos
import ReactMarkdown from "react-markdown";

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFaq, setShowFaq] = useState(true);
  const [showNewChatButton, setShowNewChatButton] = useState(false);// Nuevo estado


  const handleQuery = async () => {
    // Si la pregunta está vacía o si el sistema está cargando, no hace nada
    if (!question.trim() || isLoading) return;

    // Actualizar el estado de los mensajes para agregar la pregunta del usuario
    setMessages(prev => [...prev, { text: question, isUser: true }]);
    setIsLoading(true);
    setQuestion("");

    // Ocultar el recuadro de preguntas frecuentes cuando el usuario haga una consulta
    setShowFaq(false);
    // Mostrar el botón después de la primera interacción
    setShowNewChatButton(true); 


    try {
      // Enviar la pregunta al servidor y esperar la respuesta
      const res = await fetch("http://localhost:8000/agente", {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // El cuerpo de la solicitud está en formato JSON
        },
        body: JSON.stringify({ pregunta: question }), // Enviar la pregunta del usuario en el cuerpo de la solicitud
      });

      // Procesamos la respuesta del servidor
      const data = await res.json();

      // Limpiar el prefijo "L3##" si está presente en la respuesta
      const cleanedAnswer = data.respuesta ? data.respuesta.replace(/^L3##/i, '').trim() : "No se encontró respuesta.";

      // Por ahora se simula la respuesta del servidor
      // const data = { answer: "¡Hola! Soy el asistente virtual" };

      setMessages(prev => [...prev, { text: cleanedAnswer || "No se encontró respuesta.", isUser: false }]);
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
  const handleNewChat = async () => {

    try {
      // Notificar al backend que se quiere iniciar un nuevo chat
      const response = await fetch('/api/new-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Si se necesita enviar algun dato adicional se hace aqui
        body: JSON.stringify({ action: 'start_new_chat' }),
      });
  
      if (!response.ok) {
        throw new Error('Error al notificar al backend sobre el nuevo chat');
      }
  
      // Limpiar los campos en el frontend
      setMessages([]); // Limpia los mensajes actuales
      setShowNewChatButton(false);
      setShowFaq(true);
      console.log('Nuevo chat iniciado: Campos limpiados y backend notificado.');
    } catch (error) {
      /*
      // A modo de prueba
      setMessages([]); // Limpia los mensajes actuales
      setShowNewChatButton(false);
      setShowFaq(true);
      */
      console.error('Error al iniciar un nuevo chat:', error);
    }
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
