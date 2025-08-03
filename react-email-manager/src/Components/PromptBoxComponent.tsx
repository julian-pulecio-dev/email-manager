import React, { useState } from 'react';
import { interpretPrompt } from '../Services/InterpretPrompt';

const PromptBoxComponent = () => {
  const [texto, setText] = useState('');
  const [archivo, setArchivo] = useState(null);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setArchivo(file);

    const reader = new FileReader();
    reader.onload = () => {
      const arrayBuffer = reader.result;
    };
    reader.readAsArrayBuffer(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!texto) {
      alert("Por favor escribe un prompt.");
      return;
    }

    const formData = new FormData();
    formData.append("prompt", texto);
    if (archivo) {
      formData.append("file", archivo);
    }

    try {
      const response = await interpretPrompt(formData);
      console.log('Respuesta del servidor:', response);
    } catch (error) {
      console.error('Error al enviar el formulario:', error);
    }
  };

  return (
    <div className="formulario-container">
      <h2>Enviar Prompt con Archivo</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <div className="textarea-container">
          <textarea
            value={texto}
            onChange={handleTextChange}
            placeholder="Escribe tu mensaje aquí..."
            rows={5}
            cols={50}
          />
        </div>

        <div className="file-input-container">
          <input type="file" onChange={handleFileChange} />
        </div>

        <button type="submit" className="submit-button">
          Enviar
        </button>
      </form>
    </div>
  );
};

export default PromptBoxComponent;
