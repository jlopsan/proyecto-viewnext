import { useState } from "react";
import "./ChatInterface.css"; // Importar los estilos externos

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFaq, setShowFaq] = useState(true);

  const handleQuery = async () => {
    // Si la pregunta está vacía o si el sistema está cargando, no hace nada
    if (!question.trim() || isLoading) return;

    // Actualizar el estado de los mensajes para agregar la pregunta del usuario
    setMessages(prev => [...prev, { text: question, isUser: true }]);
    setIsLoading(true);
    setQuestion("");

    // Ocultar el recuadro de preguntas frecuentes cuando el usuario haga una consulta
    setShowFaq(false);

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

      // Por ahora se simula la respuesta del servidor
      // const data = { answer: "¡Hola! Soy el asistente virtual" };

      setMessages(prev => [...prev, { text: data.respuesta || "No se encontró respuesta.", isUser: false }]);
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

  return (
    
    <div className="chat-container">
      <header className="header">Asistente para Trámites Administrativos</header>
      <div className="chat-interface">
      {messages.length === 0 && <h1 className="title">¿Cómo puedo ayudarte?</h1>}

      <div className="chat-box">
        <div className="messages-area">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}
            >
              {message.text}
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
    <footer className="footer">Proyecto ViewNext</footer>
    </div>
  );
}
