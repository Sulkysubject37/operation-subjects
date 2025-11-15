import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from app.visualizer import create_prodigal_report

console = Console()

def run_prodigal():
    """
    Runs the Prodigal tool for prokaryotic gene prediction and generates
    a visual report summarizing the results.
    """
    try:
        # 1. Get parameters from user
        input_file = Prompt.ask("Enter the path to your input nucleotide FASTA file (e.g., genome.fasta)")
        
        output_gff = Prompt.ask("Enter the path for the output GFF annotation file", default="prodigal_genes.gff")
        output_faa = Prompt.ask("Enter the path for the output protein FASTA file", default="prodigal_proteins.faa")
        output_fna = Prompt.ask("Enter the path for the output nucleotide FASTA file", default="prodigal_nucleotides.fna")

        # 2. Construct and run the command
        command = [
            "prodigal",
            "-i", input_file,
            "-o", output_gff,
            "-a", output_faa,
            "-d", output_fna
        ]
        
        console.print(f"Running Prodigal on {input_file}... This may take some time.")
        with console.status(f"[bold green]Predicting genes with Prodigal...[/]"):
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                console.print("[bold red]Prodigal failed to run.[/bold red]")
                console.print("--- Prodigal Error Log ---")
                console.print(result.stderr)
                return

        # 3. Generate visual report
        console.print("Prodigal finished. Generating visual report...")
        html_report_path = create_prodigal_report(output_fna)

        # 4. Report success
        success_message = (
            f"[bold green]Prodigal gene prediction completed successfully![/bold green]\n\n"
            f"Predicted gene annotations (GFF) saved to:\n"
            f"  [cyan]• {os.path.abspath(output_gff)}[/cyan]\n\n"
            f"Predicted protein sequences (FASTA) saved to:\n"
            f"  [cyan]• {os.path.abspath(output_faa)}[/cyan]\n\n"
            f"Predicted gene nucleotide sequences (FASTA) saved to:\n"
            f"  [cyan]• {os.path.abspath(output_fna)}[/cyan]\n"
        )
        if html_report_path:
            success_message += f"\nVisual summary report saved to:\n  [cyan]• {os.path.abspath(html_report_path)}[/cyan]"

        console.print(Panel(success_message, title="[bold green]Prodigal Success[/bold green]"))

    except FileNotFoundError:
        console.print(f"[bold red]Error: Input file not found, or 'prodigal' command not in your PATH.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")