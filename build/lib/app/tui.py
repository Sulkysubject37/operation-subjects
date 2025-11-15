# app/tui.py

from rich.console import Console

class TUI:
    def __init__(self):
        self.console = Console()

    def show_main_menu(self):
        self.console.print("Main Menu (to be implemented)")
