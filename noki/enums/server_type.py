from enum import Enum

class ServerType(Enum):
    """Tipos de servidor disponíveis."""
    LIVE = 1
    TEST = 2
    
    @property
    def folder_name(self) -> str:
        """Retorna o nome da pasta correspondente ao tipo de servidor."""
        return {
            ServerType.LIVE: "game",
            ServerType.TEST: "staging"
        }.get(self, "game") 