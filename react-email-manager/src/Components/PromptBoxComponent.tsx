import React, { useState } from 'react';
import { interpretPrompt } from '../Services/InterpretPrompt';

const PromptBoxComponent = () => {
  const [texto, setText] = useState('');
  const [archivos, setArchivos] = useState([]); // ahora es un arreglo

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleFileChange = (e) => {
    const nuevosArchivos = Array.from(e.target.files); // convertir FileList en array
    setArchivos((prev) => [...prev, ...nuevosArchivos]);

    // Si quieres leerlos (ejemplo: para previews o validaciones)
    nuevosArchivos.forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        const arrayBuffer = reader.result;
        // podrías hacer algo con el contenido si lo necesitas
      };
      reader.readAsArrayBuffer(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!texto) {
      alert("Por favor escribe un prompt.");
      return;
    }

    const formData = new FormData();
    formData.append("prompt", texto);

    archivos.forEach((file, index) => {
      formData.append("files", file); // puedes usar "files[]" si el backend lo espera así
    });

    try {
      const response = await interpretPrompt(formData);
      console.log('Respuesta del servidor:', response);
    } catch (error) {
      console.error('Error al enviar el formulario:', error);
    }
  };

  return (
    <div className="formulario-container">
      <h2>Enviar Prompt con Archivos</h2>
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
          <input type="file" multiple onChange={handleFileChange} />
        </div>

        {/* Mostrar los archivos seleccionados */}
        {archivos.length > 0 && (
          <ul>
            {archivos.map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
        )}

        <button type="submit" className="submit-button">
          Enviar
        </button>
      </form>
    </div>
  );
};

export default PromptBoxComponent;
