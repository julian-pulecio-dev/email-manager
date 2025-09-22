import { useState, useEffect } from "react";
import { createLabel } from "../Services/CreatePrompt";
import { getLabels } from "../Services/GetLabels";

type Label = {
  id: string;
  name: string;
};

const CreateLabelComponent = () => {
  const [instruction, setInstruction] = useState("");
  const [title, setTitle] = useState("");
  const [labels, setLabels] = useState<Label[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar labels existentes
  useEffect(() => {
    const fetchLabels = async () => {
      try {
        const response = await getLabels();
        setLabels(response.data);
      } catch (err) {
        console.error("Error cargando labels:", err);
        setError("No se pudieron cargar los labels existentes");
      }
    };
    fetchLabels();
  }, []);

  // Manejar selección múltiple
  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const values = Array.from(e.target.selectedOptions, (opt) => opt.value);
    setSelected(values);
  };

const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();

  if (!instruction || !title) {
    setError("Debes completar todos los campos.");
    return;
  }

  setLoading(true);
  setError(null);

  try {
    const payload = {
      instruction,
      title,
      filtered_labels: selected,
    };

    const response = await createLabel(payload); 
    console.log("Respuesta del servidor:", response);

    setInstruction("");
    setTitle("");
    setSelected([]);
  } catch (err) {
    console.error("Error al enviar el formulario:", err);
    setError("Hubo un error al enviar el formulario.");
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="formulario-container">
      <h2>Crear label</h2>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <div className="textarea-container">
          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Escribe tu mensaje aquí..."
            rows={5}
            cols={50}
          />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Escribe el título aquí..."
          />
        </div>

        {/* Multi-select de labels existentes */}
        <div className="select-container">
          <label>Relacionar con labels existentes:</label>
          <select multiple value={selected} onChange={handleSelectChange}>
            {labels.map((label) => (
              <option key={label.id} value={label.id}>
                {label.name}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? "Enviando..." : "Enviar"}
        </button>
      </form>
    </div>
  );
};

export default CreateLabelComponent;
