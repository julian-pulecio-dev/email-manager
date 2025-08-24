from dataclasses import dataclass

@dataclass
class Attachment:
    filename: str
    content: str | bytes  # Puede ser base64 (str) o bytes
    mimetype: str = "application/octet-stream"