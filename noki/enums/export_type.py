from enum import Enum, auto

class ExportType(Enum):
    """Tipos de exportação disponíveis."""
    RAW = 1
    JSON_FILTERED = 2
    BOTH = 3
    
    @classmethod
    def from_string(cls, value: str) -> 'ExportType':
        """Converte uma string para o enum correspondente."""
        mapping = {
            'raw': cls.RAW,
            'json': cls.JSON_FILTERED,
            'both': cls.BOTH
        }
        return mapping.get(value.lower(), cls.BOTH) 