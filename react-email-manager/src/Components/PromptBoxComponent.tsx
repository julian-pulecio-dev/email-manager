import React, { useState } from 'react';
import { interpretPrompt } from '../Services/InterpretPrompt'


const PromptBoxComponent = () => {
  const [texto, setText] = useState('');

  const handleChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Aquí puedes manejar el envío del formulario
    console.log('Texto enviado:', texto);
    interpretPrompt(texto)
    // Puedes añadir lógica adicional como limpiar el textarea después del envío
    // setTexto('');
  };

  return (
    <div className="formulario-container">
      <h2>Formulario con Textarea</h2>
      <form onSubmit={handleSubmit}>
        <div className="textarea-container">
          <textarea
            value={texto}
            onChange={handleChange}
            placeholder="Escribe tu mensaje aquí..."
            rows={5}
            cols={50}
          />
        </div>
        <button type="submit" className="submit-button">
          Enviar
        </button>
      </form>
    </div>
  );
};

export default PromptBoxComponent;