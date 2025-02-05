import { useState } from "react";
import "./ChatInterface.css"; // Importar los estilos externos

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleQuery = async () => {
    if (!question.trim() || isLoading) return;

    setMessages(prev => [...prev, { text: question, isUser: true }]);
    setIsLoading(true);
    setQuestion("");

    try {
      /*
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });
      */

      //const data = await res.json();

      // Por ahora se simula la respuesta del servidor
      const data = { answer: "¡Hola! Soy el asistente virtual" };

      setMessages(prev => [...prev, { text: data.answer || "No se encontró respuesta.", isUser: false }]);
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
          <input
            type="text"
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


      <footer className="footer">Proyecto ViewNext</footer>
    </div>
    </div>
  );
}
