import re

def fix_base64_padding(image_bytes):
    """Asegura que el Base64 tenga padding correcto"""
    if isinstance(image_bytes, str):
        # Si es string, quitar prefijo 'b' si existe y espacios
        image_str = re.sub(r"^b['\"]|['\"]$", "", image_bytes.strip())
        # Añadir padding si es necesario
        padding = len(image_str) % 4
        if padding:
            image_str += "=" * (4 - padding)
        return image_str
    else:
        # Si ya es bytes, decodificar a str primero
        image_str = image_bytes.decode('utf-8')
        padding = len(image_str) % 4
        if padding:
            image_str += "=" * (4 - padding)
        return image_str