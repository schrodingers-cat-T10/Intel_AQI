import React, { useState } from 'react';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { text: 'Hello! How can I assist you today?', isBot: true },
  ]);
  const [input, setInput] = useState('');

  // Function to send message to backend and get response
  const handleSend = async (e) => {
    // Prevent page reload or form submission
    e.preventDefault();

    if (input.trim()) {
      // Add user message to chat
      setMessages((prevMessages) => [...prevMessages, { text: input, isBot: false }]);

      // Prepare request payload
      const payload = { message: input };

      try {
        // Call FastAPI backend
        const response = await fetch('http://localhost:8000/chatbot', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch the response from the server');
        }

        const data = await response.json();

        // Add chatbot's response to chat
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: data.response, isBot: true },
        ]);

      } catch (error) {
        console.error('Error:', error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Sorry, something went wrong.', isBot: true },
        ]);
      }

      // Clear input field
      setInput('');
    }
  };

  return (
    <div style={chatStyles.container}>
      <div style={chatStyles.chatBox}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...chatStyles.message,
              alignSelf: msg.isBot ? 'flex-start' : 'flex-end',
              backgroundColor: msg.isBot ? '#f1f1f1' : '#4CAF50',
              color: msg.isBot ? '#000' : '#fff',
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* Form to handle sending messages */}
      <form onSubmit={handleSend} style={chatStyles.inputContainer}>
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={chatStyles.input}
        />
        <button type="submit" style={chatStyles.sendButton}>
          <span>&#10148;</span>
        </button>
      </form>
    </div>
  );
};

const chatStyles = {
  container: {
    width: '100%',
    maxWidth: '1200px',
    height: '80vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
    marginTop: '100px', // Added margin to move the component down
  },
  chatBox: {
    flex: 1,
    padding: '20px',
    overflowY: 'scroll',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  message: {
    padding: '10px 15px',
    borderRadius: '10px',
    maxWidth: '70%',
    wordWrap: 'break-word',
  },
  inputContainer: {
    display: 'flex',
    padding: '10px',
    borderTop: '1px solid #ddd',
  },
  input: {
    flex: 1,
    padding: '10px',
    borderRadius: '5px',
    border: '1px solid #ddd',
  },
  sendButton: {
    backgroundColor: '#4CAF50',
    color: '#fff',
    border: 'none',
    borderRadius: '50%',
    padding: '10px',
    marginLeft: '10px',
    cursor: 'pointer',
  },
};

export default Chatbot;
