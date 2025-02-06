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
  // Estado para controlar si ya se envió el perfil
  const [hasProfileSent, setHasProfileSent] = useState(false);
  // Referencia para el dropdown
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

      // Solo incluir la descripción del perfil si aún no se ha enviado
      if (profileDescription && !hasProfileSent) {
        requestBody.perfil = profileDescription;
        setHasProfileSent(true); // Marcar que ya se envió la descripción
        console.log('Perfil enviado:', profileDescription);
      }

      const res = await fetch("http://localhost:8000/agente", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),  // Enviar el cuerpo con pregunta, perfil y uuid si existe
      });

      const data = await res.json();
      const cleanedAnswer = data.respuesta ? data.respuesta.replace(/^L3##/i, '').trim() : "No se encontró respuesta.";

      setMessages(prev => [...prev, { text: cleanedAnswer || "No se encontró respuesta.", isUser: false }]);

      if (!uuid) {
        setUuid(data.uuid);
      }

    } catch (error) {
      console.error("Error al enviar la pregunta:", error);
      // Si no se envia la pregunta, la descripcion vuelve a estar disponible
      setHasProfileSent(false);
      setMessages(prev => [...prev, { text: "Error al conectar con el servidor.", isUser: false, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  }, [question, uuid, isLoading, profileDescription, hasProfileSent]); // Dependencias de handleQuery


  // Para enviar consulta al presionar Enter
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
    setIsFaqSelected(false); // Resetear el estado de la selección de FAQ
    setIsProfileOpen(false); // Cerrar el dropdown del perfil
    setHasProfileSent(false); // Resetear el estado de envío del perfil

    // setProfileTitle(""); // Limpiar el título del perfil
    // setProfileDescription(""); // Limpiar la descripción del perfil

    console.log('Nuevo chat iniciado: Campos limpiados.');
  };

  // Efecto para manejar el envío de preguntas frecuentes
  useEffect(() => {
    if (isFaqSelected && question.trim()) {
      handleQuery(); // Llamamos a handleQuery cuando 'question' cambia por una FAQ
      setIsFaqSelected(false); // Resetear el estado después de que se envíe la consulta
    }
  }, [question, isFaqSelected, handleQuery]); // Depende de 'question' y 'isFaqSelected'


  // Función para manejar clics en las preguntas frecuentes
  const handleFaqClick = (faqQuestion) => {
    setQuestion(faqQuestion); // Actualizamos el estado de la pregunta
    setIsFaqSelected(true); // Indicamos que la actualización proviene de la FAQ
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
              <li onClick={() => handleFaqClick("¿Cómo puedo acceder a los trámites?")}>
                <strong>¿Cómo puedo acceder a los trámites?</strong>
              </li>
              <li onClick={() => handleFaqClick("¿Cuáles son los horarios de atención?")}>
                <strong>¿Cuáles son los horarios de atención?</strong>
              </li>
              <li onClick={() => handleFaqClick("¿Qué documentos necesito para realizar un trámite?")}>
                <strong>¿Qué documentos necesito para realizar un trámite?</strong>
              </li>
            </ul>
          </div>
        )}

      </div>
      <footer className="footer"></footer>
    </div>
  );
}
