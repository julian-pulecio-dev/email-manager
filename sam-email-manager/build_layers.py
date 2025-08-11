import os
import subprocess
import zipfile
import shutil
from pathlib import Path

# Carpeta donde están los archivos .txt
DEPENDENCIES_DIR = Path("dependencies")

def instalar_dependencias_y_zip():
    if not DEPENDENCIES_DIR.exists():
        print(f"La carpeta '{DEPENDENCIES_DIR}' no existe.")
        return

    txt_files = list(DEPENDENCIES_DIR.glob("*.txt"))

    if not txt_files:
        print("No se encontraron archivos .txt en la carpeta 'dependencies'.")
        return

    for file in txt_files:
        layer_name = file.stem  # nombre sin .txt
        layer_dir = DEPENDENCIES_DIR / layer_name
        python_dir = layer_dir / "python"

        # Crear carpetas
        python_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 Instalando dependencias para: {file.name}")
        print(f"→ Destino: {python_dir}")

        # Ejecutar pip install
        result = subprocess.run(
            ["pip", "install", "-r", str(file), "-t", str(python_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR] Falló la instalación de dependencias para {file.name}:\n{result.stderr}")
            continue

        # Crear archivo ZIP
        zip_path = DEPENDENCIES_DIR / f"{layer_name}.zip"
        print(f"🗜️  Zipeando la capa en: {zip_path}")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(python_dir):
                for f in files:
                    file_path = Path(root) / f
                    arcname = file_path.relative_to(layer_dir)  # Estructura válida para Lambda
                    zipf.write(file_path, arcname)

        # Eliminar carpeta temporal
        print(f"🧹 Eliminando carpeta temporal: {layer_dir}")
        shutil.rmtree(layer_dir)

        print(f"✅ Capa '{layer_name}' lista como {layer_name}.zip")

if __name__ == "__main__":
    instalar_dependencias_y_zip()
