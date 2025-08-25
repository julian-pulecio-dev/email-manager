import { useState } from 'react';
import { createLabel } from '../Services/CreatePrompt';

const CreateLabelComponent = () => {
  const [instruction, setInstruction] = useState('');
  const [title, setTitle] = useState('');

  const handleTextChange = (e:any) => {
    setInstruction(e.target.value);
  };

  const handleTitleChange = (e:any) => {
    setTitle(e.target.value);
  };

  const handleSubmit = async (e:any) => {
    e.preventDefault();

    if (!instruction) {
      alert("Por favor escribe un prompt.");
      return;
    }

    if (!title) {
      alert("Por favor escribe un título.");
      return;
    }

    const formData = new FormData();
    formData.append("instruction", instruction);
    formData.append("title", title);

    try {
      const response = await createLabel(formData);
      console.log('Respuesta del servidor:', response);
    } catch (error) {
      console.error('Error al enviar el formulario:', error);
    }
  };

  return (
    <div className="formulario-container">
      <h2>Crear label</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <div className="textarea-container">
          <textarea
            value={instruction}
            onChange={handleTextChange}
            placeholder="Escribe tu mensaje aquí..."
            rows={5}
            cols={50}
          />
        </div>
        <div className="input-container">
          <input
            type="text"
            value={title}
            onChange={handleTitleChange}
            placeholder="Escribe el título aquí..."
          />
        </div>
        <button type="submit" className="submit-button">
          Enviar
        </button>
      </form>
    </div>
  );
};

export default CreateLabelComponent;
