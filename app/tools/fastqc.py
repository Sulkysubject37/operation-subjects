import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def run_fastqc():
    """
    Runs the FastQC tool for quality control of sequencing data.
    It can process one or more FASTQ files.
    """
    try:
        # 1. Get parameters from user
        input_files_str = Prompt.ask("Enter paths to one or more FASTQ files (space-separated)")
        input_files = input_files_str.split()

        if not input_files:
            console.print("[bold red]No input files provided.[/bold red]")
            return

        output_dir = Prompt.ask("Enter the name for the output directory", default="fastqc_output")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # 2. Construct and run the command
        command = ["fastqc"] + input_files + ["-o", output_dir]
        
        console.print(f"Running FastQC on {len(input_files)} file(s)... This may take some time.")
        with console.status(f"[bold green]Performing FastQC analysis...[/]"):
            result = subprocess.run(command, capture_output=True, text=True)
            
            # Check if FastQC produced output HTML files
            generated_html_reports = []
            for input_file in input_files:
                base_name = os.path.basename(input_file)
                # FastQC appends _fastqc.html to the base name, handling .gz extensions automatically
                report_base = base_name.replace(".fastq.gz", "_fastqc").replace(".fq.gz", "_fastqc").replace(".fastq", "_fastqc").replace(".fq", "_fastqc")
                html_report = os.path.join(output_dir, f"{report_base}.html")
                
                if os.path.exists(html_report):
                    generated_html_reports.append(os.path.abspath(html_report))

            if not generated_html_reports:
                console.print("[bold red]FastQC failed to produce any HTML reports.[/bold red]")
                console.print("--- FastQC Error Log ---")
                console.print(result.stderr)
                return

        # 3. Report success
        success_message = (
            f"[bold green]FastQC analysis completed successfully![/bold green]\n\n"
            f"All results have been saved in the directory:\n"
            f"[yellow]{os.path.abspath(output_dir)}[/yellow]\n\n"
            f"To view the reports, open the following HTML file(s) in your web browser:\n"
        )
        for report_path in generated_html_reports:
            success_message += f"  [cyan]• {report_path}[/cyan]\n"

        console.print(Panel(success_message, title="[bold green]FastQC Success[/bold green]"))

    except FileNotFoundError:
        console.print(f"[bold red]Error: One or more input files not found, or 'fastqc' command not in your PATH.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")