from .llm_client import LLMClient  # Changed import
from .logger import Logger


class ProblemAnalyzer:
    def __init__(self, llm_client, logger):
        self.llm_client = llm_client
        self.logger = logger
        
    def identify_components(self, problem):
        prompt = f"""
        You are a reasoning agent tasked with solving the following problem:
        {problem}

        Identify the key components of the problem and break it down into its core elements.
        """
        response = self.llm_client.call_llm(prompt)
        full_response = self.logger.stream_response(response)
        return [component.strip() for component in full_response.split("\n") if component.strip()]
        
    def generate_hypotheses(self, problem):
        prompt = f"""
        You are a reasoning agent tasked with solving the following problem:
        {problem}

        Generate a list of 'what-if' hypotheses that explore possible solutions or intermediate scenarios.
        """
        response = self.llm_client.call_llm(prompt)
        full_response = self.logger.stream_response(response)
        return full_response.split("\n")