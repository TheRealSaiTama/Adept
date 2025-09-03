import typer
from rich.console import Console
from rich.panel import Panel
from adept.core.engine import run_write_task
from adept.commands.config import MODEL_CONFIG

console = Console()
app = typer.Typer(add_completion=False)

@app.command("execute")
def execute_command(
    task: str = typer.Argument(..., help="Your coding/task request"),
    provider: str = typer.Option("groq", "--provider", "-p", help="API provider to use"),
    model: str = typer.Option("default", "--model", "-m", help="Model alias to use")
):
    """Executes an AI task using the core engine."""
    
    model_full_name = MODEL_CONFIG[provider]["models"].get(model, MODEL_CONFIG[provider]["models"]["default"])
    console.print(Panel(f"Using [bold]{provider}:{model_full_name}[/bold] (alias: '{model}')", title="✅ Model Selected"))
    
    try:
        output = run_write_task(task=task, provider=provider, model=model)
        console.print("\n[bold green]AI Response:[/bold green]")
        console.print(Panel(output, title=f"📝 {provider} Output"))
    except Exception as e:
        console.print(Panel(f"[red]Error: {str(e)}[/red]", title="🔥 Execution Failed"))
