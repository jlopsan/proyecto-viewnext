import { useState, useRef, useEffect, useCallback } from "react";
import "./ChatInterface.css"; // Importar los estilos externos
import ReactMarkdown from "react-markdown";

export default function ChatInterface() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFaq, setShowFaq] = useState(true);
  const [showNewChatButton, setShowNewChatButton] = useState(false);
  // Agregar estado para el UUID
  const [uuid, setUuid] = useState(null);  
  // Nuevos estados para el perfil
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [profileTitle, setProfileTitle] = useState("");
  const [profileDescription, setProfileDescription] = useState("");
  const [hasProfileSent, setHasProfileSent] = useState(false);
  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);
  // Estado para seleccion de preguntas frecuentes
  const [isFaqSelected, setIsFaqSelected] = useState(false);

  
  // Función para guardar el perfil
  const handleSaveProfile = () => {
    console.log('Profile saved:', { profileTitle, profileDescription });
    setIsProfileOpen(false);
  };

  // Función para manejar la tecla Enter en el perfil (para guardar)
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


  // Función para enviar la pregunta al agente
  const handleQuery = useCallback(async () => {
    if (!question.trim() || isLoading) return;
  
    // Agregar mensaje visible al chat (solo la pregunta del usuario)
    setMessages(prev => [...prev, { text: question, isUser: true }]);
    setIsLoading(true);
    setQuestion("");
  
    setShowFaq(false);
    setShowNewChatButton(true);
  
    try {
      // Preparar el prompt que se enviará al backend
      const requestBody = { pregunta: question };
  
      // Solo agregar el UUID si existe
      if (uuid) {
        requestBody.uuid = uuid;
      }
  
      // Solo incluir la descripción del perfil si aún no se ha enviado
      if (profileDescription && !hasProfileSent) {
        requestBody.perfil = profileDescription;
        setHasProfileSent(true); // Marcar que ya se envió la descripción
      }
  
      // Console log para verificar el prompt
      console.log('Prompt enviado al backend:', requestBody);
  
      const res = await fetch("http://localhost:8000/agente", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody), // Enviar pregunta, perfil y UUID si aplica
      });
  
      const data = await res.json();
      const cleanedAnswer = data.respuesta ? data.respuesta.replace(/^L3##/i, '').trim() : "No se encontró respuesta.";
  
      // Agregar respuesta del asistente al chat
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
        body: JSON.stringify(consulta),
      });
    } catch (error) {
      console.error("Error al guardar la consulta en la base de datos:", error);
    }

      if (!uuid) {
        // Guardar UUID si no existe
        setUuid(data.uuid); 
      }
  
    } catch (error) {
      console.error("Error al enviar la pregunta:", error);
      // Restablecer para permitir reintento si falla
      setHasProfileSent(false);
      setMessages(prev => [...prev, { text: "Error al conectar con el servidor.", isUser: false, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  }, [question, uuid, isLoading, profileDescription, hasProfileSent]); 
  


  // Para enviar consulta al presionar Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleQuery();
    }
  };

  // Función para iniciar un nuevo chat
  const handleNewChat = () => {
    // Limpiar los campos en el frontend
    setMessages([]); 
    setQuestion("");
    setUuid(null);
    setShowNewChatButton(false); 
    setShowFaq(true); 
    setIsLoading(false); 
    setIsFaqSelected(false); 
    setIsProfileOpen(false); 
    setHasProfileSent(false); 

    console.log('Nuevo chat iniciado: Campos limpiados.');
  };

  // Efecto para manejar el envío de preguntas frecuentes
  useEffect(() => {
    if (isFaqSelected && question.trim()) {
      handleQuery(); 
      setIsFaqSelected(false); 
    }
  }, [question, isFaqSelected, handleQuery]); 


  // Función para manejar clics en las preguntas frecuentes
  const handleFaqClick = (faqQuestion) => {
    setQuestion(faqQuestion); 
    setIsFaqSelected(true); 
  };

  return (
    <div className="chat-container">
      <header className="header" style={{ display: 'flex', alignItems: 'center', fontSize: '1.5rem', gap: '10px' }}>
      <img 
        src="/favicon.png" 
        alt="AsesorIA Logo" 
        style={{ 
          width: '50px', 
          height: '50px', 
          objectFit: 'contain' 
        }} 
      />
      <div>
        AsesorIA
        <div className="subtitle" style={{ fontSize: '1rem' }}>Proyecto ViewNext</div>
      </div>
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
              <li onClick={() => handleFaqClick("¿Cuáles son los requisitos para solicitar una beca universitaria?")}>
                <strong> ¿Cuáles son los requisitos para solicitar una beca universitaria?</strong>
              </li>
              <li onClick={() => handleFaqClick("¿Cómo puedo calcular cuánto me corresponde de prestación por desempleo?")}>
                <strong>¿Cómo puedo calcular cuánto me corresponde de prestación por desempleo?</strong>
              </li>
              <li onClick={() => handleFaqClick("¿Qué documentos necesito para hacer la declaración de la renta?")}>
                <strong>¿Qué documentos necesito para hacer la declaración de la renta?</strong>
              </li>
            </ul>
          </div>
        )}

      </div>
      <footer className="footer"></footer>
    </div>
  );
}
