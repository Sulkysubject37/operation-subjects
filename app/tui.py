from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

class TUI:
    """
    A class to handle the Text-based User Interface for the bioinformatics suite.
    """
    def __init__(self):
        """
        Initializes the TUI with a rich Console.
        """
        self.console = Console()

    def show_main_menu(self):
        """
        Displays the main menu and returns the user's choice.

        Returns:
            str: The user's selected menu option.
        """
        self.console.clear()
        self.console.print(Panel(
            Text("Operation Subjects: A TUI-based Bioinformatics Suite", justify="center", style="bold cyan"),
            border_style="green"
        ))
        
        menu_text = (
            "[bold]1.[/bold] [cyan]BLAST[/cyan] - Search for homologous sequences.\n"
            "[bold]2.[/bold] [cyan]MEME[/cyan] - Discover motifs in sequences.\n"
            "[bold]3.[/bold] [cyan]MAFFT[/cyan] - Perform a Multiple Sequence Alignment.\n"
            "[bold]4.[/bold] [cyan]ClustalOmega[/cyan] - Perform a Multiple Sequence Alignment.\n"
            "[bold]5.[/bold] [cyan]FastQC[/cyan] - Perform quality control on FASTQ files.\n"
            "[bold]6.[/bold] [cyan]FastP[/cyan] - Preprocess FASTQ files (trimming, filtering).\n"
            "[bold]7.[/bold] [cyan]Prodigal[/cyan] - Predict genes in prokaryotic genomes.\n"
            "[bold]8.[/bold] [cyan]Phylogenetic Analysis[/cyan] - Automated pipeline (BLAST -> MSA -> Tree).\n"
            "[bold]q.[/bold] [red]Quit[/red]"
        )
        
        self.console.print(Panel(menu_text, title="Main Menu", border_style="blue"))
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "q"], default="1")
        return choice

    def show_blast_menu(self):
        """
        Displays the BLAST menu to get parameters from the user.

        Returns:
            tuple: A tuple containing the query file path, database name, and output file path.
        """
        self.console.print(Panel("BLAST Search", style="bold yellow"))
        query_file = Prompt.ask("Enter the path to your query FASTA file")
        db_name = Prompt.ask("Enter the database to search against", choices=["nr", "nt", "swissprot"], default="nr")
        output_file = Prompt.ask("Enter the path for the output XML file", default="blast_results.xml")
        return query_file, db_name, output_file

    def show_phylogeny_source_menu(self):
        """
        Asks the user to choose the source for the phylogenetic analysis.

        Returns:
            str: The user's choice ('single' or 'multi').
        """
        self.console.print(Panel("Phylogenetic Analysis Source", style="bold yellow"))
        source = Prompt.ask(
            "Start from a single sequence (and find homologs with BLAST) or a multi-sequence file?",
            choices=["single", "multi"],
            default="single"
        )
        return source
