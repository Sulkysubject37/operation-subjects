import os
import io
import base64
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend to prevent GUI windows
import matplotlib.pyplot as plt
from Bio.Blast import NCBIXML
from Bio import AlignIO, SeqIO
from rich.console import Console

console = Console()

def _plot_to_base64(fig):
    """
    Converts a matplotlib figure to a base64 encoded PNG image string.

    Args:
        fig: The matplotlib figure object to convert.

    Returns:
        str: A base64 encoded string representing the PNG image.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig) # Close the figure to free up memory
    return img_str

def create_blast_html_report(xml_file_path: str):
    """
    Parses a BLAST XML file and generates a user-friendly HTML report with plots.

    Args:
        xml_file_path (str): The path to the BLAST XML output file.

    Returns:
        str: The path to the generated HTML report, or an error message string.
    """
    html_file_path = os.path.splitext(xml_file_path)[0] + ".html"
    
    try:
        with open(xml_file_path, "r") as xml_handle:
            blast_records = list(NCBIXML.parse(xml_handle))

        with open(html_file_path, "w") as html_handle:
            # --- HTML Header and CSS ---
            html_handle.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>BLAST Results</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
                <style>
                    body { font-family: 'Roboto', sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }
                    .container { max-width: 1000px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #0056b3; text-align: center; margin-bottom: 30px; }
                    h2 { color: #0056b3; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 40px; }
                    h3 { color: #0056b3; margin-top: 25px; }
                    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                    th, td { border: 1px solid #e0e0e0; padding: 12px; text-align: left; }
                    th { background-color: #e9f5ff; font-weight: 700; color: #0056b3; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    tr:hover { background-color: #f0f8ff; }
                    .alignment { background-color: #fdfdfd; border: 1px solid #e0e0e0; padding: 15px; margin-bottom: 15px; border-radius: 5px; overflow-x: auto; }
                    .alignment pre { margin: 0; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.9em; line-height: 1.4; }
                    .plot-container { text-align: center; margin: 30px 0; }
                    .plot-container img { max-width: 100%; height: auto; border: 1px solid #e0e0e0; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>BLAST Search Report</h1>
            ")

            if not blast_records:
                html_handle.write("<p>No BLAST records found.</p></div></body></html>")
                return html_file_path
            
            for blast_record in blast_records:
                html_handle.write(f"<h2>Query: {blast_record.query}</h2>")
                
                if not blast_record.alignments:
                    html_handle.write("<p>No alignments found for this query.</p>")
                    continue

                all_e_values = [hsp.expect for alignment in blast_record.alignments for hsp in alignment.hsps]
                all_scores = [hsp.score for alignment in blast_record.alignments for hsp in alignment.hsps]

                # --- E-value Plot ---
                if all_e_values:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.hist(all_e_values, bins=20, color='#007bff', edgecolor='black')
                    ax.set_title('E-value Distribution')
                    ax.set_xlabel('E-value')
                    ax.set_ylabel('Frequency')
                    ax.set_yscale('log')
                    html_handle.write("<h3>E-value Distribution</h3>")
                    html_handle.write(f"<div class='plot-container'><img src='data:image/png;base64,{_plot_to_base64(fig)}' alt='E-value Distribution'></div>")

                # --- Score Plot ---
                if all_scores:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.hist(all_scores, bins=20, color='#28a745', edgecolor='black')
                    ax.set_title('Score Distribution')
                    ax.set_xlabel('Score')
                    ax.set_ylabel('Frequency')
                    html_handle.write("<h3>Score Distribution</h3>")
                    html_handle.write(f"<div class='plot-container'><img src='data:image/png;base64,{_plot_to_base64(fig)}' alt='Score Distribution'></div>")

                # --- Summary Table ---
                html_handle.write("<h2>Summary of Top Hits</h2>")
                html_handle.write("<table><tr><th>Description</th><th>Score</th><th>E-value</th><th>Identity (%)</th><th>Query Coverage (%)</th></tr>")
                for alignment in blast_record.alignments[:20]: # Top 20 hits
                    hsp = alignment.hsps[0]
                    identity = (hsp.identities / hsp.align_length) * 100 if hsp.align_length else 0
                    query_coverage = (hsp.query_end - hsp.query_start + 1) / blast_record.query_length * 100 if blast_record.query_length else 0
                    html_handle.write(f"<tr><td>{alignment.title}</td><td>{hsp.score:.2f}</td><td>{hsp.expect:.2e}</td><td>{identity:.2f}</td><td>{query_coverage:.2f}</td></tr>")
                html_handle.write("</table>")

                # --- Detailed Alignments ---
                html_handle.write("<h2>Detailed Alignments</h2>")
                for alignment in blast_record.alignments[:10]: # Top 10 alignments
                    html_handle.write(f"<h3>{alignment.title}</h3>")
                    for hsp in alignment.hsps:
                        html_handle.write(f"<div class='alignment'><pre>" \
                                          f"<b>Score:</b> {hsp.score:.2f}, <b>E-value:</b> {hsp.expect:.2e}\n" \
                                          f"<b>Identities:</b> {hsp.identities}/{hsp.align_length} ({identity:.2f}%)\n" \
                                          f"<b>Query coverage:</b> {query_coverage:.2f}%\n\n" \
                                          f"Query: {hsp.query_start:<5} {hsp.query} {hsp.query_end}\n" \
                                          f"       {'':<5} {hsp.match}\n" \
                                          f"Sbjct: {hsp.sbjct_start:<5} {hsp.sbjct} {hsp.sbjct_end}" \
                                          f"</pre></div>")
                
            html_handle.write("</div></body></html>")
        
        return html_file_path

    except Exception as e:
        console.print(f"[bold red]Could not generate BLAST HTML report: {e}[/bold red]")
        return None

def create_prodigal_report(nucleotide_fasta_path: str):
    """
    Parses a Prodigal nucleotide FASTA file and generates an HTML report
    with plots for gene length and GC content distribution.

    Args:
        nucleotide_fasta_path (str): Path to the Prodigal-generated nucleotide FASTA file.

    Returns:
        str or None: The path to the generated HTML report, or None if an error occurred.
    """
    html_file_path = os.path.splitext(nucleotide_fasta_path)[0] + "_report.html"

    try:
        sequences = list(SeqIO.parse(nucleotide_fasta_path, "fasta"))
        if not sequences:
            console.print("[yellow]Warning: No sequences found in Prodigal output to generate a report.[/yellow]")
            return None

        gene_lengths = [len(seq.seq) for seq in sequences]
        gc_contents = [(seq.seq.count('G') + seq.seq.count('C')) / len(seq.seq) * 100 for seq in sequences if len(seq.seq) > 0]

        # --- Gene Length Plot ---
        fig_len, ax_len = plt.subplots(figsize=(10, 5))
        ax_len.hist(gene_lengths, bins=50, color='#007bff', edgecolor='black')
        ax_len.set_title('Predicted Gene Length Distribution')
        ax_len.set_xlabel('Gene Length (bp)')
        ax_len.set_ylabel('Frequency')
        ax_len.grid(axis='y', linestyle='--', alpha=0.7)
        len_plot_base64 = _plot_to_base64(fig_len)

        # --- GC Content Plot ---
        fig_gc, ax_gc = plt.subplots(figsize=(10, 5))
        ax_gc.hist(gc_contents, bins=50, color='#28a745', edgecolor='black')
        ax_gc.set_title('Predicted Gene GC Content Distribution')
        ax_gc.set_xlabel('GC Content (%)')
        ax_gc.set_ylabel('Frequency')
        ax_gc.grid(axis='y', linestyle='--', alpha=0.7)
        gc_plot_base64 = _plot_to_base64(fig_gc)

        # --- HTML Generation ---
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Prodigal Report</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Roboto', sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }}
                .container {{ max-width: 90%; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1, h2 {{ color: #0056b3; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                .plot-container {{ text-align: center; margin: 30px 0; }}
                .plot-container img {{ max-width: 100%; height: auto; border: 1px solid #e0e0e0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Prodigal Gene Prediction Report</h1>
                <h2>Gene Length Distribution</h2>
                <div class="plot-container"><img src="data:image/png;base64,{len_plot_base64}" alt="Gene Length Distribution"></div>
                <h2>GC Content Distribution</h2>
                <div class="plot-container"><img src="data:image/png;base64,{gc_plot_base64}" alt="GC Content Distribution"></div>
            </div>
        </body>
        </html>
        """

        with open(html_file_path, "w") as f:
            f.write(html_template)
        
        return html_file_path

    except Exception as e:
        console.print(f"[bold red]Could not generate Prodigal HTML report: {e}[/bold red]")
        return None
