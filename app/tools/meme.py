import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from Bio import SeqIO

console = Console()

def run_meme():
    """
    Runs the MEME tool for motif discovery. It automatically detects if the
    input is a single sequence and applies the correct model.
    """
    try:
        # 1. Get parameters from user
        input_file = Prompt.ask("Enter the path to your FASTA file (can contain single or multiple sequences)")
        output_dir = Prompt.ask("Enter the name for the output directory", default="meme_output")

        # 2. Count sequences to determine the correct MEME model
        try:
            with open(input_file) as f:
                num_sequences = sum(1 for _ in SeqIO.parse(f, "fasta"))
        except FileNotFoundError:
            console.print(f"[bold red]Error: Input file not found at '{input_file}'[/bold red]")
            return
        
        if num_sequences == 0:
            console.print("[bold red]Error: Input file contains no sequences.[/bold red]")
            return

        # 3. Construct and run the command
        command = ["meme", input_file, "-o", output_dir]
        if num_sequences == 1:
            command.extend(["-mod", "anr"])
            console.print("[yellow]Single sequence detected. Using 'Any Number of Repetitions' model (-mod anr).[/yellow]")

        console.print(f"Running MEME... This may take some time depending on your file size.")
        with console.status(f"[bold green]Discovering motifs with MEME...[/]"):
            result = subprocess.run(command, capture_output=True, text=True)
            
            html_output_path = os.path.join(output_dir, "meme.html")
            if not os.path.exists(html_output_path):
                console.print("[bold red]MEME failed to produce an output file.[/bold red]")
                console.print("--- MEME Error Log ---")
                console.print(result.stderr)
                return

        # 4. Report success
        success_message = (
            f"[bold green]MEME analysis completed successfully![/bold green]\n\n"
            f"All results have been saved in the directory:\n"
            f"[yellow]{os.path.abspath(output_dir)}[/yellow]\n\n"
            f"To view the primary report, open this file in your web browser:\n"
            f"[cyan]{os.path.abspath(html_output_path)}[/cyan]"
        )

        console.print(Panel(success_message, title="[bold green]MEME Success[/bold green]"))

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")