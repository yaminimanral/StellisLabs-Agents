import os

class Config:
    MAX_RECURSION_DEPTH = 3
    MAX_SUBAGENTS_PER_LEVEL = 3
    COST_THRESHOLD = 10
    TIME_LIMIT = 600
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    
    EVALUATION_WEIGHTS = {
        'feasibility': 0.3,
        'impact': 0.25,
        'cost_efficiency': 0.25,
        'time_to_implement': 0.2
    }
    
    SIMULATION_PARAMS = {
        'implementation_success_rate': 0.85,
        'resource_availability': 0.75,
        'market_conditions': 0.8,
        'risk_factor': 0.15
    }