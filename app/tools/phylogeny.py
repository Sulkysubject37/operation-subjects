import os
import subprocess
import tempfile
from Bio.Blast import NCBIXML
from Bio.Blast.Applications import NcbiblastpCommandline
from Bio import SeqIO, AlignIO, Phylo
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import matplotlib.pyplot as plt

console = Console()

def _get_sequences_from_blast(query_file: str, num_hits: int = 20):
    """
    Performs a remote BLAST, gets top hits, and returns their sequences.
    """
    # ... (Implementation for fetching sequences via BLAST)
    # This would be a complex function involving remote BLAST, parsing, and fetching.
    # For this example, we'll simulate it by returning a path to a multi-fasta file.
    # In a real implementation, this would generate a temporary multi-fasta file.
    pass # Placeholder for the complex BLAST fetching logic

def run_phylogenetic_analysis(tui):
    """
    Runs a full phylogenetic analysis pipeline:
    BLAST -> MSA -> Phylogenetic Tree.
    """
    try:
        source = tui.show_phylogeny_source_menu()
        
        if source == 'single':
            query_file = Prompt.ask("Enter the path to your single-sequence FASTA file")
            # Here you would call a function like _get_sequences_from_blast
            # For now, we'll print a message and exit as it's a complex feature.
            console.print("[yellow]Feature to fetch homologs via BLAST is not fully implemented in this version.[/yellow]")
            console.print("Please start with a multi-sequence FASTA file.")
            return
        else: # multi
            msa_input_file = Prompt.ask("Enter the path to your multi-sequence FASTA file")

        # Create a temporary directory to store intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            alignment_file = os.path.join(temp_dir, "alignment.fasta")
            
            # 1. Perform MSA using MAFFT
            console.print("Performing Multiple Sequence Alignment with MAFFT...")
            with console.status("[bold green]Aligning sequences...[/]"):
                mafft_command = ["mafft", "--auto", msa_input_file]
                with open(alignment_file, "w") as out_f:
                    subprocess.run(mafft_command, stdout=out_f, stderr=subprocess.PIPE, check=True)

            # 2. Construct Phylogenetic Tree
            console.print("Constructing phylogenetic tree...")
            with console.status("[bold green]Building tree...[/]"):
                align = AlignIO.read(alignment_file, "fasta")
                
                # Using UPGMA for tree construction
                from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
                calculator = DistanceCalculator('identity')
                dm = calculator.get_distance(align)
                constructor = DistanceTreeConstructor(calculator, 'upgma')
                tree = constructor.build_tree(align)
                
                # Prettify tree
                for clade in tree.find_clades():
                    if clade.name:
                        clade.name = clade.name[:30] # Truncate long names
                
                # 3. Visualize and save the tree
                fig = plt.figure(figsize=(10, 15), dpi=100)
                axes = fig.add_subplot(1, 1, 1)
                Phylo.draw(tree, axes=axes, do_show=False)
                
                output_image_path = "phylogenetic_tree.png"
                fig.savefig(output_image_path)
                plt.close(fig)

        success_message = (
            f"[bold green]Phylogenetic analysis completed successfully![/bold green]\n\n"
            f"The phylogenetic tree has been saved as an image to:\n"
            f"[cyan]{os.path.abspath(output_image_path)}[/cyan]"
        )
        console.print(Panel(success_message, title="[bold green]Phylogeny Success[/bold green]"))

    except FileNotFoundError:
        console.print("[bold red]Error: Input file not found or a required command (e.g., 'mafft') is not in your PATH.[/bold red]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]An error occurred during an external command:[/bold red]\n{e.stderr}")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red]\n{e}")