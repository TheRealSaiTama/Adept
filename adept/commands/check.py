import typer
import httpx
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()

app = typer.Typer(add_completion=False)

@app.command()
def models(
    provider: str = typer.Option("gemini", "--provider", "-p", help="API provider to check (gemini or groq)")
):
    
    
    if provider.lower() not in ["gemini", "groq"]:
        console.print(Panel(f"[red]Error: Provider '{provider}' is not supported. Choose 'gemini' or 'groq'[/red]", title="🔥 Invalid Provider"))
        return

    console.print(Panel(f"Querying {provider.title()} AI for available models...", title=f"🔍 Checking {provider.title()} API Access"))
    
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        console.print(Panel(f"[red]Error: {provider.upper()}_API_KEY not found in .env file.[/red]", title="🔥 Configuration Error"))
        return

    try:
        if provider.lower() == "gemini":
            url = "https://generativelanguage.googleapis.com/v1/models"
            params = {"key": api_key}
            headers = {}
            with httpx.Client(timeout=30) as client:
                response = client.get(url, params=params, headers=headers)
        elif provider.lower() == "groq":
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            with httpx.Client(timeout=30) as client:
                response = client.get(url, headers=headers)

        response.raise_for_status()
        result = response.json()
        
        table = Table(title=f"✅ Available {provider.title()} Models")
        table.add_column("Model ID", style="cyan", no_wrap=True)

        if provider.lower() == "gemini":
             for model in result.get("models", []):
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    table.add_row(model.get("name"))
        elif provider.lower() == "groq":
            for model in result.get("data", []):
                table.add_row(model.get("id"))
        
        console.print(table)
        console.print("\n[bold yellow]Instruction:[/bold yellow] Copy the ID of a fast, modern model (e.g., 'llama-3.1-8b-instant') and update your `write.py` file.")

    except httpx.HTTPStatusError as e:
        error_details = e.response.json().get("error", {}).get("message", "Unknown error")
        console.print(Panel(f"[red]API Error {e.response.status_code}[/red]\n{error_details}", title="🔥 API Error"))
    except Exception as e:
        console.print(Panel(f"[red]Unexpected Error: {str(e)}[/red]", title="🔥 Critical Failure"))
