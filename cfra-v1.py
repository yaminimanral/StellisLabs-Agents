import os
import time
import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Initialize Rich console for formatted output
console = Console()

# Configurable parameters
COST_THRESHOLD = 15  # Maximum number of API calls allowed
TIME_LIMIT = 1200  # Increased time limit to 20 minutes (1200 seconds)
MAX_SCENARIOS = 3  # Maximum number of scenarios to generate and evaluate

# Global counters
api_call_count = 0
start_time = time.time()

# Default LLM API endpoint (can be modular)
LLM_API_URL = "http://localhost:11434/api/generate"

class CounterfactualAgent:
    def __init__(self, question):
        self.question = question
        self.scenarios = []
        self.results = []
        self.console = Console()

    def log(self, message, style="bold blue"):
        """Log messages with Rich formatting."""
        self.console.print(Panel(Text(message, style=style)))

    def log_markdown(self, markdown_text):
        """Render Markdown content in the console."""
        markdown = Markdown(markdown_text)
        self.console.print(markdown)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((json.JSONDecodeError, KeyError)),
    )
    def call_llm(self, prompt):
        """Call the LLM API with the given prompt."""
        global api_call_count
        if api_call_count >= COST_THRESHOLD:
            raise Exception("Cost threshold exceeded. Stopping further API calls.")
        if time.time() - start_time > TIME_LIMIT:
            raise Exception("Time limit exceeded. Stopping execution.")

        api_call_count += 1
        try:
            response = requests.post(
                LLM_API_URL,
                json={"model": "llama3.1:latest", "prompt": prompt, "stream": True},
                stream=True,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            self.log(f"Error calling LLM API: {e}", style="bold red")
            raise

    def validate_json(self, chunk):
        """Validate if the chunk is a valid JSON object."""
        try:
            chunk_data = json.loads(chunk.decode("utf-8"))
            if "response" not in chunk_data:
                raise KeyError("Missing 'response' key in JSON.")
            return chunk_data
        except (json.JSONDecodeError, KeyError) as e:
            self.log(f"Invalid JSON response: {e}", style="bold yellow")
            raise

    def stream_response(self, response):
        """Stream the response from the LLM API."""
        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                try:
                    chunk_data = self.validate_json(chunk)
                    chunk_content = chunk_data.get("response", "")
                    full_response += chunk_content
                except (json.JSONDecodeError, KeyError):
                    self.log("Retrying due to invalid JSON response...", style="bold yellow")
                    raise
        return full_response

    def generate_scenarios(self):
        """Generate 'what-if' hypotheses for the given question."""
        prompt = f"""
        You are a reasoning agent. The question is:
        {self.question}

        Generate a list of {MAX_SCENARIOS} 'what-if' scenarios to explore alternative outcomes. Include logical assumptions and clear hypotheses.
        """
        try:
            response = self.call_llm(prompt)
            full_response = self.stream_response(response)
            self.scenarios = full_response.split("\n")[:MAX_SCENARIOS]  # Limit scenarios
        except Exception as e:
            self.log(f"Error generating scenarios: {e}", style="bold red")

    def evaluate_scenario(self, scenario):
        """Evaluate the impact of a single scenario."""
        prompt = f"""
        You are a reasoning agent. The scenario is:
        {scenario}

        Use logical reasoning and probabilistic models to evaluate the impact of this scenario. Provide detailed insights.
        """
        try:
            response = self.call_llm(prompt)
            full_response = self.stream_response(response)
            self.results.append({"scenario": scenario, "evaluation": full_response})
        except Exception as e:
            self.log(f"Error evaluating scenario: {e}", style="bold red")

    def summarize_recommendation(self):
        """Summarize the evaluations into a final recommendation."""
        if not self.results:
            return "No valid scenarios were evaluated."

        # Combine all evaluations into a single prompt for summarization
        combined_evaluations = "\n".join([result["evaluation"] for result in self.results])
        prompt = f"""
        You are a reasoning agent. Below are the evaluations of multiple scenarios:
        {combined_evaluations}

        Summarize the key insights and provide a clear, actionable recommendation based on the analysis.
        """
        try:
            response = self.call_llm(prompt)
            full_response = self.stream_response(response)
            return full_response
        except Exception as e:
            self.log(f"Error summarizing recommendation: {e}", style="bold red")
            return "Failed to generate a recommendation."

    def explore_counterfactuals(self):
        """Explore all generated counterfactual scenarios."""
        self.generate_scenarios()

        # Show a progress indicator while evaluating scenarios
        with Live(Spinner("dots"), refresh_per_second=15) as live:
            live.update(Panel(Text("Generating scenarios...", style="bold blue")))
            for i, scenario in enumerate(self.scenarios):
                if scenario.strip():
                    live.update(Panel(Text(f"Evaluating scenario {i + 1}/{len(self.scenarios)}: {scenario}", style="bold green")))
                    self.evaluate_scenario(scenario)

    def display_final_recommendation(self):
        """Display only the final recommendation."""
        recommendation = self.summarize_recommendation()
        self.log_markdown("# Final Recommendation")
        self.log_markdown(recommendation)

# Main function to run the counterfactual agent
def main():
    question = "What if we increase the marketing budget by 20% for our new product launch?"
    agent = CounterfactualAgent(question)

    # Start the timer
    start_time = time.time()
    agent.explore_counterfactuals()
    elapsed_time = time.time() - start_time

    # Display the final recommendation and elapsed time
    agent.display_final_recommendation()
    agent.log(f"Time taken: {elapsed_time:.2f} seconds", style="bold green")

if __name__ == "__main__":
    main()