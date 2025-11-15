from app.tui import TUI
from app.tools.blast import run_blast
from app.tools.phylogeny import run_phylogenetic_analysis
from app.tools.msa import run_msa
from app.tools.meme import run_meme
from app.tools.fastqc import run_fastqc
from app.tools.fastp import run_fastp
from app.tools.prodigal import run_prodigal

def main():
    """
    Main function to run the TUI and handle user menu choices.
    """
    tui = TUI()
    
    while True:
        choice = tui.show_main_menu()
        
        if choice == "1":
            query_file, db_name, output_file = tui.show_blast_menu()
            run_blast(query_file, db_name, output_file)
        elif choice == "2":
            run_meme()
        elif choice == "3":
            run_msa("mafft")
        elif choice == "4":
            run_msa("clustalo")
        elif choice == "5":
            run_fastqc()
        elif choice == "6":
            run_fastp()
        elif choice == "7":
            run_prodigal()
        elif choice == "8":
            run_phylogenetic_analysis(tui)
        elif choice == "q":
            break
        
        # Pause to allow user to see the output before clearing the screen
        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()
