import numpy as np
from .config import Config

class OutcomeSimulator:
    def __init__(self, simulation_params):
        self.params = simulation_params
        
    def simulate_outcomes(self, hypotheses):
        outcomes = []
        for hypothesis in hypotheses:
            base_prob = self.params['implementation_success_rate']
            resource_factor = self.params['resource_availability']
            market_factor = self.params['market_conditions']
            risk_adjustment = 1 - self.params['risk_factor']
            
            outcome_score = (base_prob * resource_factor * market_factor * risk_adjustment)
            hypothesis_length = len(hypothesis.split())
            complexity_factor = np.clip(hypothesis_length / 100, 0.5, 1.5)
            
            final_score = np.clip(outcome_score * complexity_factor, 0, 1)
            outcomes.append((hypothesis, round(final_score, 2)))
        return outcomes