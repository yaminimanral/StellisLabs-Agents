import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live

class Logger:
    def __init__(self):
        self.console = Console()

    def log(self, message, style="bold blue"):
        self.console.print(Panel(Text(message, style=style), expand=False))

    def log_markdown(self, markdown_text):
        markdown = Markdown(markdown_text)
        self.console.print(Panel(markdown, style="dim", expand=False))

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
        full_response = ""
        with Live(refresh_per_second=15) as live:
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = self.validate_json(chunk)
                        chunk_content = chunk_data.get("response", "")
                        full_response += chunk_content
                        live.update(Panel(Markdown(full_response), title="Streaming Response", style="bold green"))
                    except:
                        self.log("Retrying due to invalid JSON response...", style="bold yellow")
                        raise
        return full_response