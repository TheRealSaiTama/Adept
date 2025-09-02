import typer
import httpx
import os
import re
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import lancedb
from sentence_transformers import SentenceTransformer


load_dotenv()
console = Console()

app = typer.Typer(add_completion=False)

from adept.commands.write import MODEL_CONFIG

@app.command("execute")
def execute_chain(
    task_list: str = typer.Argument(..., help="A numbered list of tasks to execute in sequence."),
    provider: str = typer.Option("gemini", "--provider", "-p", help="API provider to use (gemini or groq)"),
    model: str = typer.Option("default", "--model", "-m", help="Model alias to use"),
    context: bool = typer.Option(False, "--context", "-c", help="Enable context-aware RAG for the first task only.")
):
    
    tasks = [task.strip() for task in re.split(r'\s*\d+\.\s*', task_list) if task.strip()]
    
    if not tasks:
        console.print(Panel("[red]Error: No tasks found in the provided list.[/red]", title="🔥 Parsing Error"))
        return
        
    console.print(f"Executing [bold cyan]{len(tasks)}[/bold cyan] tasks in sequence:")
    for i, task in enumerate(tasks, 1):
        console.print(f"  [yellow]{i}. {task}[/yellow]")
    console.print("\n" + "="*50 + "\n")

    conversation_history = []
    
    for i, task in enumerate(tasks, 1):
        console.print(f"Executing Task {i}: {task}")

        if i == 1 and context:
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
                if results:
                    context_parts = []
                    for result in results:
                        context_part = f"""--- CONTEXT FROM {result['path']} ---
{result['text']}
--- END CONTEXT ---"""
                        context_parts.append(context_part)
                    context_string = "\n\n".join(context_parts)
                    task = f"{context_string}\n\nNow, based on the above context, please address the following task:\n{task}"
                    console.print(f"[green]Added context from {len(results)} code chunks.[/green]")
                else:
                    console.print("[yellow]Warning: No relevant context found.[/yellow]")
            except Exception as e:
                console.print(Panel(f"[red]Error during RAG retrieval: {str(e)}[/red]", title="🔥 RAG Error"))
                return

        prompt = "\n".join(conversation_history) + f"\n\nPrevious tasks are complete. Now, perform this task: {task}"

        config = MODEL_CONFIG[provider]
        model_name = config["models"].get(model, config["models"]["default"])
        api_key = os.getenv(f"{provider.upper()}_API_KEY")

        try:
            if provider == "gemini":
                gemini_history = []
                for turn in range(0, len(conversation_history), 2):
                    gemini_history.append({"role": "user", "parts": [{"text": conversation_history[turn]}]})
                    if turn + 1 < len(conversation_history):
                        gemini_history.append({"role": "model", "parts": [{"text": conversation_history[turn+1]}]})
                gemini_history.append({"role": "user", "parts": [{"text": task}]})
                payload = {"contents": gemini_history}
                url = config["url_template"].format(model_name=model_name)
                headers = {"Content-Type": "application/json"}
                params = {"key": api_key}

            elif provider == "groq":
                groq_history = []
                for turn in range(0, len(conversation_history), 2):
                    groq_history.append({"role": "user", "content": conversation_history[turn]})
                    if turn + 1 < len(conversation_history):
                        groq_history.append({"role": "assistant", "content": conversation_history[turn+1]})
                groq_history.append({"role": "user", "content": task})
                payload = {"messages": groq_history, "model": model_name}
                url = config["url_template"]
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                params = None

            with httpx.Client(timeout=60) as client:
                response = client.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                result = response.json()

            if provider == "gemini":
                output = result["candidates"][0]["content"]["parts"][0]["text"]
            elif provider == "groq":
                output = result["choices"][0]["message"]["content"]
            
            console.print(f"Response for Task {i}:")
            console.print(Panel(output, title=f"📝 {provider} Output - Step {i}"))
            console.print("\n" + "="*50 + "\n")

            conversation_history.append(task)
            conversation_history.append(output)

        except Exception as e:
            console.print(Panel(f"[red]Error during task {i}: {e}[/red]", title="🔥 Chain Execution Failed"))
            break

    console.print("[bold green]✅ All tasks completed successfully![/bold green]")
