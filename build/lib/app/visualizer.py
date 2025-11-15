# app/visualizer.py

from rich.console import Console

class Visualizer:
    def __init__(self):
        self.console = Console()

    def display_table(self, data):
        self.console.print("Table view (to be implemented)")
