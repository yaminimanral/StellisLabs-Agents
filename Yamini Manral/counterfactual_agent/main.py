# main.py
from rich.console import Console
from src.conversation import ChatSession

console = Console()


def main():
    chat = ChatSession()
    chat.start()
    # question = "What if we use an agile development model instead of a waterfall model for our software project?"
    # question = "What if I choose to invest in real estate rather than the stock market for my long-term wealth growth?"
    # question = "What if we launch a new seasonal product during the holiday season to boost sales?"
    # question = "What if the government introduces free healthcare for all, funded by increased taxes?"
    # console.print("\n[bold black]Question: ", question, "\n")

    # start_time = time()
    # agent = CounterfactualAgent(question)

    # try:
    #     # Call the evaluation method
    #     agent.explore_counterfactuals()

    # except Exception as e:
    #     console.print(f"[bold red]Error:[/bold red] {e}")

    # agent.display_final_recommendation()
    
    # elapsed_time = time() - start_time
    # print("\n")
    # log_markdown(f"Time taken: {elapsed_time:.2f} seconds")
    # print("\n")

if __name__ == "__main__":
    main()
