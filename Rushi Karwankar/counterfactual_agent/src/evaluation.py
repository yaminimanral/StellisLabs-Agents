import numpy as np
from .config import Config

class HypothesisEvaluator:
    def __init__(self, weights):
        self.weights = weights
        
    def evaluate_hypothesis_criteria(self, hypothesis):
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
        evaluations = []
        for hypothesis in hypotheses:
            criteria_scores = self.evaluate_hypothesis_criteria(hypothesis)
            weighted_score = sum(
                criteria_scores[criterion] * weight 
                for criterion, weight in self.weights.items()
            )
            evaluations.append((hypothesis, round(weighted_score, 2)))
        return evaluations
