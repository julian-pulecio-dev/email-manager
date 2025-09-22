import { useEffect, useState } from "react";
import { getLabels } from "../Services/GetLabels"; // 👈 ajusta el import a tu servicio real

type Label = {
  id: string;
  name: string; // o "name" si tu API lo devuelve así
};

const MultiSelectLabels = () => {
  const [labels, setLabels] = useState<Label[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLabels = async () => {
      setLoading(true);
      try {
        const response = await getLabels();
        setLabels(Array.from(response.data)); // asegúrate de que `response` sea un array [{id, title}]
      } catch (err) {
        console.error("Error al cargar labels:", err);
        setError("No se pudieron cargar los labels");
      } finally {
        setLoading(false);
      }
    };
    fetchLabels();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const options = Array.from(e.target.selectedOptions, (opt) => opt.value);
    setSelected(options);
    console.log("Seleccionados:", options);
  };

  return (
    <div className="labels-container">
      <h2>Selecciona Labels</h2>
      {loading && <p>Cargando labels...</p>}
      {error && <p className="error-message">{error}</p>}

      <select
        multiple
        value={selected}
        onChange={handleChange}
        className="multi-select"
      >
        {labels.map((label) => (
          <option key={label.id} value={label.id}>
            {label.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default MultiSelectLabels;
