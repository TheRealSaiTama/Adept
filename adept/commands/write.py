import typer
import httpx
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import lancedb
from sentence_transformers import SentenceTransformer

load_dotenv()
console = Console()

app = typer.Typer(add_completion=False)

MODEL_CONFIG = {
    "gemini": {
        "url_template": "https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent",
        "models": {
            "default": "gemini-1.5-pro",
            "pro": "gemini-1.5-pro",
            "flash": "gemini-1.5-flash",
        }
    },
    "groq": {
        "url_template": "https://api.groq.com/openai/v1/chat/completions",
        "models": {
            "default": "llama-3.1-8b-instant",
            "llama3-8b": "llama-3.1-8b-instant",
            "llama3-70b": "llama-3.1-70b-versatile",
            "mixtral": "mixtral-8x7b-32768",
            "gemma": "gemma2-9b-it",
        }
    }
}

@app.command("execute")
def execute_command(
    task: str = typer.Argument(..., help="Your coding/task request"),
    provider: str = typer.Option("gemini", "--provider", "-p", help="API provider to use (gemini or groq)"),
    model: str = typer.Option("default", "--model", "-m", help="Model alias to use (e.g., pro, flash, llama3-8b)"),
    context: bool = typer.Option(False, "--context", "-c", help="Enable context-aware RAG from the local index.")
):
    
    if context:
        try:
            console.print("[blue]Loading embedding model for RAG...[/blue]")
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            db_path = "./.adept_db"
            if not os.path.exists(db_path):
                console.print(Panel("[red]Error: No index found. Please run 'adept index create' first.[/red]", title="🔥 RAG Error"))
                return
                
            db = lancedb.connect(db_path)
            
            if "codebase" not in db.table_names():
                console.print(Panel("[red]Error: No codebase table found in index.[/red]", title="🔥 RAG Error"))
                return
                
            table = db.open_table("codebase")
            
            console.print("[blue]Creating embedding for your task...[/blue]")
            task_embedding = embedder.encode(task)
            
            console.print("[blue]Searching for relevant context...[/blue]")
            results = table.search(task_embedding).limit(3).to_list()
            
            if not results:
                console.print("[yellow]Warning: No relevant context found.[/yellow]")
            else:
                context_parts = []
                for result in results:
                    context_part = f"""--- CONTEXT FROM {result['path']} ---
{result['text']}
--- END CONTEXT ---"""
                    context_parts.append(context_part)
                
                context_string = "\n\n".join(context_parts)
                task = f"{context_string}\n\nNow, based on the above context, please address the following task:\n{task}"
                console.print(f"[green]Added context from {len(results)} code chunks.[/green]")
                
        except Exception as e:
            console.print(Panel(f"[red]Error during RAG retrieval: {str(e)}[/red]", title="🔥 RAG Error"))
            return
    
    if provider not in MODEL_CONFIG:
        console.print(Panel(f"[red]Error: Provider '{provider}' is not supported. Choose from {list(MODEL_CONFIG.keys())}[/red]", title="🔥 Configuration Error"))
        return
        
    config = MODEL_CONFIG[provider]
    
    model_name = config["models"].get(model, config["models"]["default"])
    
    console.print(Panel(f"Using [bold]{provider}:{model_name}[/bold] (alias: '{model}') | {provider.title()} Production API", title="✅ Model Selected"))
    
    api_key = os.getenv(f"{provider.upper()}_API_KEY")
    if not api_key:
        console.print(Panel(f"[red]Error: {provider.upper()}_API_KEY not found in .env file.[/red]", title="🔥 Configuration Error"))
        return

    try:
        if provider == "gemini":
            url = config["url_template"].format(model_name=model_name)
            headers = {"Content-Type": "application/json"}
            params = {"key": api_key}
            payload = {"contents": [{"parts": [{"text": task}]}]}
        elif provider == "groq":
            url = config["url_template"]
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            params = None
            payload = {"messages": [{"role": "user", "content": task}], "model": model_name}

        with httpx.Client(timeout=30) as client:
            response = client.post(url, json=payload, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()

            if provider == "gemini":
                output = result["candidates"][0]["content"]["parts"][0]["text"]
            elif provider == "groq":
                output = result["choices"][0]["message"]["content"]
            
            console.print("\n")
            console.print(f"[bold green]AI Response:[/bold green]")
            console.print(Panel(output, title=f"📝 {provider} Output"))
            
    except httpx.HTTPStatusError as e:
        error_details = e.response.json().get("error", {}).get("message", "Unknown error")
        console.print(Panel(f"[red]API Error {e.response.status_code}[/red]\n{error_details}", title="🔥 API Error"))
    except Exception as e:
        console.print(Panel(f"[red]Unexpected Error: {str(e)}[/red]", title="🔥 Critical Failure"))