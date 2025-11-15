import os
import subprocess
from Bio.Blast import NCBIWWW
from rich.console import Console
from rich.panel import Panel
from app.visualizer import create_blast_html_report

console = Console()

def run_blast(query_file: str, db_name: str, output_file: str):
    """
    Performs a remote BLAST search using NCBIWWW and generates an HTML report.

    Args:
        query_file (str): Path to the input FASTA file.
        db_name (str): Name of the BLAST database (e.g., 'nr', 'nt').
        output_file (str): Path to save the BLAST XML output.
    """
    try:
        with open(query_file, "r") as f:
            fasta_sequence = f.read()

        console.print(f"Running remote BLAST search against '{db_name}' database... This may take a while.")
        with console.status("[bold green]Searching...[/]"):
            result_handle = NCBIWWW.qblast(program="blastn", database=db_name, sequence=fasta_sequence)
            
            with open(output_file, "w") as out_handle:
                out_handle.write(result_handle.read())
            
            result_handle.close()

        console.print(f"BLAST XML output saved to [cyan]{output_file}[/cyan]. Generating HTML report...")
        
        # Generate HTML report from the XML output
        html_report_path = create_blast_html_report(output_file)
        
        success_message = (
            f"[bold green]BLAST search completed successfully![/bold green]\n"
            f"XML results saved to [cyan]{output_file}[/cyan]\n"
        )
        if html_report_path:
            success_message += f"Visual HTML report saved to [cyan]{html_report_path}[/cyan]"

        console.print(Panel(success_message, title="[bold green]BLAST Success[/bold green]"))

    except FileNotFoundError:
        console.print(f"[bold red]Error: Query file not found at '{query_file}'[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred during BLAST search:[/bold red]\n{e}")
