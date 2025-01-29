import os
import time
import requests
import json
import numpy as np
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configurable parameters for optimization
MAX_RECURSION_DEPTH = 3
MAX_SUBAGENTS_PER_LEVEL = 3
COST_THRESHOLD = 10
TIME_LIMIT = 600

# Global counters for tracking resources
api_call_count = 0
start_time = time.time()

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

class CounterfactualReasoningAgent:
    def __init__(self, max_sub_agents=5, max_depth=3, task_timeout=60):
        self.console = Console()
        self.max_sub_agents = max_sub_agents
        self.max_depth = max_depth
        self.task_timeout = task_timeout
        # Weights for different evaluation criteria
        self.evaluation_weights = {
            'feasibility': 0.3,
            'impact': 0.25,
            'cost_efficiency': 0.25,
            'time_to_implement': 0.2
        }
        # Parameters for simulation model
        self.simulation_params = {
            'implementation_success_rate': 0.85,
            'resource_availability': 0.75,
            'market_conditions': 0.8,
            'risk_factor': 0.15
        }

    def log(self, message, style="bold blue"):
        """Log messages with Rich formatting."""
        self.console.print(Panel(Text(message, style=style), expand=False))

    def log_markdown(self, markdown_text):
        """Render Markdown content in the console."""
        markdown = Markdown(markdown_text)
        self.console.print(Panel(markdown, style="dim", expand=False))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((json.JSONDecodeError, KeyError)),
    )
    def call_llm(self, prompt):
        """Call the Ollama API with the given prompt."""
        global api_call_count
        if api_call_count >= COST_THRESHOLD:
            raise Exception("Cost threshold exceeded. Stopping further API calls.")
        if time.time() - start_time > TIME_LIMIT:
            raise Exception("Time limit exceeded. Stopping execution.")

        api_call_count += 1
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": "llama3.1:latest",
                    "prompt": prompt,
                    "stream": True,
                },
                stream=True,
            )
            response.raise_for_status()
            return response
        except Exception as e:
            self.log(f"Error calling Ollama API: {e}", style="bold red")
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
        """Stream the response from the Ollama API."""
        full_response = ""
        with Live(refresh_per_second=15) as live:
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = self.validate_json(chunk)
                        chunk_content = chunk_data.get("response", "")
                        full_response += chunk_content
                        live.update(Panel(Markdown(full_response), title="Streaming Response", style="bold green"))
                    except (json.JSONDecodeError, KeyError):
                        self.log("Retrying due to invalid JSON response...", style="bold yellow")
                        raise
        return full_response

    def identify_key_components(self, problem):
        """Step 1: Identify the key components of the problem."""
        prompt = f"""
        You are a reasoning agent tasked with solving the following problem:
        {problem}

        Identify the key components of the problem and break it down into its core elements.
        """
        try:
            response = self.call_llm(prompt)
            full_response = self.stream_response(response)
            components = full_response.split("\n")
            return [component.strip() for component in components if component.strip()]
        except Exception as e:
            self.log(f"Error identifying key components: {e}", style="bold red")
            return []

    def generate_hypotheses(self, problem):
        """Step 2: Generate 'what-if' hypotheses."""
        prompt = f"""
        You are a reasoning agent tasked with solving the following problem:
        {problem}

        Generate a list of 'what-if' hypotheses that explore possible solutions or intermediate scenarios.
        """
        try:
            response = self.call_llm(prompt)
            full_response = self.stream_response(response)
            return full_response.split("\n")
        except Exception as e:
            self.log(f"Error generating hypotheses: {e}", style="bold red")
            return []

    def evaluate_hypothesis_criteria(self, hypothesis):
        """Evaluate a hypothesis based on multiple criteria."""
        words = hypothesis.lower().split()
        
        feasibility_keywords = {'implement', 'practical', 'realistic', 'achievable', 'possible'}
        feasibility = min(1.0, len([w for w in words if w in feasibility_keywords]) * 0.2)
        
        impact_keywords = {'improve', 'optimize', 'enhance', 'increase', 'reduce', 'efficiency'}
        impact = min(1.0, len([w for w in words if w in impact_keywords]) * 0.2)
        
        cost_keywords = {'cost', 'budget', 'expensive', 'affordable', 'savings', 'reduce'}
        cost_efficiency = min(1.0, len([w for w in words if w in cost_keywords]) * 0.2)
        
        time_keywords = {'quick', 'immediate', 'long-term', 'phase', 'gradual', 'timeline'}
        time_to_implement = min(1.0, len([w for w in words if w in time_keywords]) * 0.2)
        
        return {
            'feasibility': feasibility,
            'impact': impact,
            'cost_efficiency': cost_efficiency,
            'time_to_implement': time_to_implement
        }

    def evaluate_hypotheses(self, hypotheses):
        """Step 3: Evaluate hypotheses using domain-specific metrics."""
        evaluations = []
        for hypothesis in hypotheses:
            criteria_scores = self.evaluate_hypothesis_criteria(hypothesis)
            weighted_score = sum(
                criteria_scores[criterion] * weight 
                for criterion, weight in self.evaluation_weights.items()
            )
            evaluations.append((hypothesis, round(weighted_score, 2)))
        return evaluations

    def simulate_outcomes(self, hypotheses):
        """Step 4: Simulate outcomes using a deterministic model."""
        outcomes = []
        for hypothesis in hypotheses:
            base_prob = self.simulation_params['implementation_success_rate']
            resource_factor = self.simulation_params['resource_availability']
            market_factor = self.simulation_params['market_conditions']
            risk_adjustment = 1 - self.simulation_params['risk_factor']
            
            outcome_score = (base_prob * resource_factor * market_factor * risk_adjustment)
            hypothesis_length = len(hypothesis.split())
            complexity_factor = np.clip(hypothesis_length / 100, 0.5, 1.5)
            
            final_score = np.clip(outcome_score * complexity_factor, 0, 1)
            outcomes.append((hypothesis, round(final_score, 2)))
        return outcomes

    def provide_insights(self, evaluations, outcomes):
        """Step 5: Provide insights and recommendations."""
        # Combine evaluation and simulation scores
        combined_scores = []
        for ((hyp1, eval_score), (_, sim_score)) in zip(evaluations, outcomes):
            combined_score = (eval_score + sim_score) / 2
            combined_scores.append((hyp1, combined_score))
        
        # Sort by combined score and get top 2 recommendations
        top_recommendations = sorted(combined_scores, key=lambda x: x[1], reverse=True)[:2]
        
        recommendations_text = "### Final Recommendations:\n\n"
        for i, (hypothesis, _) in enumerate(top_recommendations, 1):
            recommendations_text += f"{i}. {hypothesis}\n"
        
        self.log_markdown(recommendations_text)

    def solve(self, problem):
        """Solve the problem."""
        self.log_markdown(f"## Analyzing problem: {problem}")

        # Step 1: Identify key components
        components = self.identify_key_components(problem)
        if components:
            self.log_markdown(f"### Key Components:\n{', '.join(components)}")

        # Step 2: Generate hypotheses
        hypotheses = self.generate_hypotheses(problem)

        # Step 3: Evaluate hypotheses
        evaluations = self.evaluate_hypotheses(hypotheses)

        # Step 4: Simulate outcomes
        outcomes = self.simulate_outcomes(hypotheses)

        # Step 5: Provide insights
        self.provide_insights(evaluations, outcomes)

# Main function
if __name__ == "__main__":
    agent = CounterfactualReasoningAgent()
    problem_statement = "How to optimize the supply chain to reduce costs and improve efficiency?"
    agent.solve(problem_statement)