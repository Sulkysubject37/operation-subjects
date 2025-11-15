import subprocess
import os
import html
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from Bio import AlignIO
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def _plot_to_base64(fig):
    """Converts a matplotlib figure to a base64 encoded PNG image."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def _calculate_conservation(alignment):
    """
    Calculates a simple conservation score for each column of an alignment.
    The score is the frequency of the most common character in that column.
    """
    conservation = []
    for i in range(alignment.get_alignment_length()):
        col = alignment[:, i]
        if not col:
            conservation.append(0)
            continue
        
        unique_chars = set(col)
        most_common_char = max(unique_chars, key=col.count)
        freq = col.count(most_common_char) / len(col)
        conservation.append(freq)
    return conservation

def _generate_msa_static_report(alignment_file: str):
    """
    Generates a static HTML report for an MSA, including a conservation plot.

    Args:
        alignment_file (str): Path to the alignment file (FASTA format).

    Returns:
        str or None: The path to the generated HTML report, or None on failure.
    """
    html_file_path = os.path.splitext(alignment_file)[0] + ".html"
    
    try:
        alignment = AlignIO.read(alignment_file, "fasta")
        
        # 1. Calculate and plot conservation
        conservation = _calculate_conservation(alignment)
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.bar(range(len(conservation)), conservation, color='#007bff', width=1.0)
        ax.set_title('Sequence Conservation Plot')
        ax.set_xlabel('Alignment Position')
        ax.set_ylabel('Conservation Score (Frequency of Most Common Character)')
        ax.set_ylim(0, 1)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plot_base64 = _plot_to_base64(fig)

        # 2. Get the alignment as a formatted string
        alignment_buffer = io.StringIO()
        AlignIO.write(alignment, alignment_buffer, "fasta")
        alignment_str = html.escape(alignment_buffer.getvalue())

        # 3. Generate HTML
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>MSA Report</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Roboto', sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }}
                .container {{ max-width: 90%; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #0056b3; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .plot-container {{ text-align: center; margin: 30px 0; }}
                .plot-container img {{ max-width: 100%; height: auto; border: 1px solid #e0e0e0; border-radius: 5px; }}
                pre {{ background-color: #222; color: #fff; padding: 15px; border-radius: 5px; white-space: pre; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Multiple Sequence Alignment Report</h1>
                <h2>Conservation Plot</h2>
                <div class="plot-container"><img src="data:image/png;base64,{plot_base64}" alt="Conservation Plot"></div>
                <h2>Alignment</h2>
                <pre>{alignment_str}</pre>
            </div>
        </body>
        </html>
        """

        with open(html_file_path, "w") as f:
            f.write(html_template)
        
        return html_file_path

    except Exception as e:
        console.print(f"[bold red]Could not generate MSA HTML report: {e}[/bold red]")
        return None


def run_msa(tool_name: str):
    """
    Runs a Multiple Sequence Alignment tool (MAFFT or ClustalOmega) and
    generates a static HTML report with a conservation plot.

    Args:
        tool_name (str): The name of the MSA tool to run ('mafft' or 'clustalo').
    """
    try:
        input_file = Prompt.ask("Enter the path to your multi-sequence FASTA file")
        output_file = Prompt.ask("Enter the path for the output alignment file", default=f"{tool_name}_alignment.fasta")

        if tool_name == "mafft":
            command = ["mafft", "--auto", input_file]
        elif tool_name == "clustalo":
            command = ["clustalo", "-i", input_file, "-o", output_file, "--force"]
        else:
            console.print(f"[bold red]Unknown MSA tool: {tool_name}[/bold red]")
            return

        console.print(f"Running {tool_name.upper()}...")
        with console.status(f"[bold green]Performing {tool_name.upper()} alignment...[/]"):
            if tool_name == "mafft":
                with open(output_file, "w") as out_f:
                    subprocess.run(command, stdout=out_f, stderr=subprocess.PIPE, check=True)
            else: # clustalo
                subprocess.run(command, capture_output=True, text=True, check=True)

        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            console.print(f"[bold red]Error: The alignment tool '{tool_name}' did not produce an output file.[/bold red]")
            console.print("This can happen if the input file contains only one sequence or is not a valid FASTA file.")
            return

        console.print(f"Alignment calculation completed. Generating report...")
        html_report_path = _generate_msa_static_report(output_file)

        success_message = (
            f"[bold green]MSA completed successfully![/bold green]\n"
            f"Alignment file saved to [cyan]{output_file}[/cyan]\n"
        )
        if html_report_path:
            success_message += f"Static HTML report saved to [cyan]{html_report_path}[/cyan]"

        console.print(Panel(success_message, title=f"[bold green]{tool_name.upper()} Success[/bold green]"))

    except FileNotFoundError:
        console.print(f"[bold red]Error: Input file not found or '{tool_name}' command not in your PATH.[/bold red]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]An error occurred while running {tool_name}:[/bold red]\n{e.stderr}")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")