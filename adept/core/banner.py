from rich.console import Console
from rich.text import Text

def print_banner() -> None:
    """Prints a gradient ASCII art banner for the application."""
    console = Console()
    art = r"""
 █████╗ ██████╗ ███████╗██████╗ ████████╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████║██║  ██║█████╗  ██████╔╝   ██║   
██╔══██║██║  ██║██╔══╝  ██         ██║   
██║  ██║██████╔╝███████╗██║        ██║   
╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝        ╚═╝   
    """
    
    # Create a Text object with gradient colors
    styled_art = Text(art)
    styled_art.stylize("bold cyan", 0, len(art))
    
    # Print the styled text, centered in the terminal
    console.print(styled_art, justify="center")
    console.print() # Add a blank line for spacing

