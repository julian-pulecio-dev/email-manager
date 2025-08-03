from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)
logger.setLevel('DEBUG')

@dataclass
class File:
    """Represents a file with its name and content."""
    filename: str
    content: str
    content_type: str 
