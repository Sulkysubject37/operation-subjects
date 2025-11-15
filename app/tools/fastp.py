import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def run_fastp():
    """
    Runs the FastP tool for preprocessing of FASTQ files.
    It supports both single-end and paired-end reads.
    """
    try:
        # 1. Ask user for read type
        read_type = Prompt.ask("Is your data single-end or paired-end?", choices=["single", "paired"], default="paired")
        
        command = ["fastp"]
        output_files = []

        # 2. Get parameters based on read type
        if read_type == "single":
            in1 = Prompt.ask("Enter the path to your input FASTQ file")
            out1 = Prompt.ask("Enter the path for the output cleaned FASTQ file", default="cleaned.fastq")
            command.extend(["-i", in1, "-o", out1])
            output_files.append(out1)
        else: # paired-end
            in1 = Prompt.ask("Enter the path to your forward read file (R1)")
            in2 = Prompt.ask("Enter the path to your reverse read file (R2)")
            out1 = Prompt.ask("Enter the path for the output forward cleaned file", default="cleaned_R1.fastq")
            out2 = Prompt.ask("Enter the path for the output reverse cleaned file", default="cleaned_R2.fastq")
            command.extend(["-i", in1, "-I", in2, "-o", out1, "-O", out2])
            output_files.extend([out1, out2])

        html_report = Prompt.ask("Enter the name for the HTML report file", default="fastp_report.html")
        json_report = Prompt.ask("Enter the name for the JSON report file", default="fastp_report.json")
        command.extend(["-h", html_report, "-j", json_report])
        
        # 3. Run the command
        console.print(f"Running FastP... This may take some time.")
        with console.status(f"[bold green]Preprocessing reads with FastP...[/]"):
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                console.print("[bold red]FastP failed to run.[/bold red]")
                console.print("--- FastP Error Log ---")
                console.print(result.stderr)
                return

        # 4. Report success
        output_files_str = "\n".join([f"  [cyan]• {os.path.abspath(f)}[/cyan]" for f in output_files])
        success_message = (
            f"[bold green]FastP preprocessing completed successfully![/bold green]\n\n"
            f"Cleaned FASTQ file(s) saved to:\n{output_files_str}\n\n"
            f"To view the quality report, open this file in your web browser:\n"
            f"  [cyan]• {os.path.abspath(html_report)}[/cyan]"
        )

        console.print(Panel(success_message, title="[bold green]FastP Success[/bold green]"))

    except FileNotFoundError:
        console.print(f"[bold red]Error: One or more input files not found, or 'fastp' command not in your PATH.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")