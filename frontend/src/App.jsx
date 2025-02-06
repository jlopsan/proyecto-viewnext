import { useState, useRef, useEffect } from "react";
import "./ChatInterface.css"; // Importar los estilos externos
import ReactMarkdown from "react-markdown";

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFaq, setShowFaq] = useState(true);
  const [showNewChatButton, setShowNewChatButton] = useState(false);
  const [uuid, setUuid] = useState(null);  // Agregar estado para el UUID
  // Nuevos estados para el perfil
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [profileTitle, setProfileTitle] = useState("");
  const [profileDescription, setProfileDescription] = useState("");

    // Referencia para el dropdown
    const dropdownRef = useRef(null);
    const buttonRef = useRef(null);
  
  // Función para guardar el perfil
  const handleSaveProfile = () => {
    // Añadir funcionalidad para el backend
    console.log('Profile saved:', { profileTitle, profileDescription });
    setIsProfileOpen(false);
  };

  // Función para manejar la tecla Enter
  const handleProfileKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSaveProfile();
    }
  };

  // Efecto para manejar clics fuera del dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isProfileOpen && 
          dropdownRef.current && 
          !dropdownRef.current.contains(event.target) &&
          !buttonRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isProfileOpen]);

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
    setUuid(null); // Limpiar el UUID cuando se empieza un nuevo chat
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

      <button 
        ref={buttonRef}
        className="profile-button"
        onClick={() => setIsProfileOpen(!isProfileOpen)}
      >
        Perfil
      </button>

      {isProfileOpen && (
        <div className="profile-dropdown" ref={dropdownRef}>
          <div>
            <label className="profile-label">
              Título
            </label>
            <input
              type="text"
              value={profileTitle}
              onChange={(e) => setProfileTitle(e.target.value)}
              onKeyDown={handleProfileKeyDown}
              className="profile-input"
              placeholder="Introduce un título"
            />
          </div>
          <div>
            <label className="profile-label">
              Descripción
            </label>
            <textarea
              value={profileDescription}
              onChange={(e) => setProfileDescription(e.target.value)}
              onKeyDown={handleProfileKeyDown}
              className="profile-textarea"
              placeholder="Describe tu perfil"
            />
          </div>
          <div className="profile-buttons">
            <button 
              onClick={() => setIsProfileOpen(false)}
              className="profile-button-cancel"
            >
              Cancelar
            </button>
            <button 
              onClick={handleSaveProfile}
              className="profile-button-save"
            >
              Guardar
            </button>
          </div>
        </div>
      )}

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
