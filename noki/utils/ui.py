import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.logging import RichHandler
from rich.theme import Theme

# Configuração do tema
theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green"
})

console = Console(theme=theme)

def setup_logging():
    """Configura o logging com formatação rica."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[]
    )

def create_progress() -> Progress:
    """Cria uma barra de progresso customizada."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    )

def print_banner():
    """Exibe o banner do aplicativo."""
    banner = r"""
[cyan]
     █████╗  ██████╗    ███╗   ██╗ ██████╗ ██╗  ██╗██╗
    ██╔══██╗██╔═══██╗   ████╗  ██║██╔═══██╗██║ ██╔╝██║
    ███████║██║   ██║   ██╔██╗ ██║██║   ██║█████╔╝ ██║
    ██╔══██║██║   ██║   ██║╚██╗██║██║   ██║██╔═██╗ ██║
    ██║  ██║╚██████╔╝   ██║ ╚████║╚██████╔╝██║  ██╗██║
    ╚═╝  ╚═╝ ╚═════╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
                        Dumper
            A.O. Noki - The Official Project
               https://github.com/AO-Noki
[/cyan]
    """
    console.print(banner) 