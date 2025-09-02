import typer
import os
import pathlib
import lancedb
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import math

console = Console()
app = typer.Typer(add_completion=False)

IGNORE_DIRS = {'.git', '__pycache__', '.venv', '.adept_db', '.DS_Store', 'node_modules', 'venv', 'env'}
IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac', '.zip', '.tar', '.gz', '.rar', '.7z'}

def should_ignore_path(path: pathlib.Path) -> bool:
    
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True

    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True

    return False

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
        if end == len(text):
            break

    return chunks

@app.command("create")
def create_index():
    
    console.print("[blue]Loading sentence transformer model...[/blue]")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        console.print(f"[red]Error loading sentence transformer model: {e}[/red]")
        return

    console.print("[blue]Initializing LanceDB...[/blue]")
    try:
        db_path = "./.adept_db"
        db = lancedb.connect(db_path)
    except Exception as e:
        console.print(f"[red]Error connecting to LanceDB: {e}[/red]")
        return

    console.print("[blue]Scanning directory for files...[/blue]")
    try:
        current_dir = pathlib.Path(".")
        files = []

        for file_path in current_dir.rglob("*"):
            if file_path.is_file() and not should_ignore_path(file_path):
                files.append(file_path)

        if not files:
            console.print("[yellow]No files found to index.[/yellow]")
            return

        console.print(f"[green]Found {len(files)} files to process.[/green]")
    except Exception as e:
        console.print(f"[red]Error scanning directory: {e}[/red]")
        return

    data_to_insert = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        file_task = progress.add_task("[cyan]Processing files...", total=len(files))

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if not content.strip():
                    progress.advance(file_task)
                    continue

                chunks = chunk_text(content)

                embeddings = model.encode(chunks)

                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    data_to_insert.append({
                        "id": f"{file_path}#{i}",
                        "text": chunk,
                        "path": str(file_path),
                        "vector": embedding
                    })

                progress.advance(file_task)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not process {file_path}: {e}[/yellow]")
                progress.advance(file_task)
                continue

    console.print("[blue]Creating database table...[/blue]")
    try:
        if "codebase" in db.table_names():
            db.drop_table("codebase")

        table = db.create_table("codebase", data=data_to_insert, mode="overwrite")
        console.print(f"[green]Successfully indexed {len(data_to_insert)} chunks into database.[/green]")
    except Exception as e:
        console.print(f"[red]Error creating database table: {e}[/red]")
        return

    console.print("[bold green]✅ Indexing completed successfully![/bold green]")