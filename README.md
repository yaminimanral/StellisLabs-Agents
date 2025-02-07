# 🤖 **Counterfactual Reasoning Agent**
A sophisticated Python-based agent that explores and evaluates "what-if" scenarios using Large Language Models (LLMs). This tool helps generate, analyze, and provide recommendations for counterfactual scenarios in decision-making processes.

## 📁 **Repository Structure**
StellisLabs-Agents <br> 
 ├── Yamini Manral <br>
 │ ├── counterfactual_agent/ <br>
 │ ├──── agent.py        # Main agent implementation <br>
 │ ├──── main.py         # Entry point of the application <br>
 │ ├──── utils.py        # Utility functions <br>
 │ ├──── scenario.py     # Scenario generation and handling <br>
 │ ├──── llm_api.py      # LLM API interaction layer <br>
 │ ├──── logger.py       # Logging configuration <br>
 │ └──── config.py       # Configuration settings <br>
 ├── README.md <br>

**agent.py**: Core CounterfactualAgent class implementation <br>
**main.py**: Application entry point and runtime configuration <br>
**utils.py:** Helper functions and utilities <br>
**scenario.py:** Scenario generation and evaluation logic <br>
**llm_api.py:** LLM API integration and response handling <br>
**logger.py:** Logging setup and management <br>
**config.py:** Configuration constants and settings <br>

## ✨ Features

- Generate multiple "what-if" scenarios for a given question
- Evaluate each scenario using logical reasoning and probabilistic models
- Stream responses from LLM API with proper error handling
- Rich console output with formatted text and progress indicators
- Automatic retry mechanism for API calls
- Cost and time limit controls
- Comprehensive logging system

### 🎯 Scenario Generation

- Automatically generates multiple "what-if" scenarios based on the input question
- Limits the number of scenarios to prevent resource exhaustion
- Validates and processes each scenario individually

### 📊 Evaluation System

- Evaluates each scenario using LLM-powered analysis
- Provides detailed insights and potential impacts
- Combines evaluations for comprehensive recommendations

### 🛡️ Error Handling & Resilience

- Implements retry mechanism for API calls
- Handles JSON validation and processing errors
- Includes timeout and cost threshold controls

### 💻 Rich Console Output

- Progress indicators during scenario evaluation
- Formatted text output with color coding
- Markdown rendering support
- Comprehensive logging system

### ⚠️ Error Handling
The agent includes robust error handling:

🔄 Retries failed API calls up to 3 times
⏱️ Exponential backoff between retry attempts
✅ JSON validation for API responses
💰 Cost threshold monitoring
⌛ Time limit enforcement

### 📝 Logging
All operations are logged both to the console and a logfile.txt file, including:

📊 Scenario generation and evaluation progress
⚠️ Error messages and warnings
📋 Final recommendations
⏱️ Execution time

## 📄 License
This project is licensed under the MIT License.

## 👤 Author
Yamini Manral


