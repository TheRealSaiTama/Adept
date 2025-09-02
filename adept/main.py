import typer
from adept.commands import write, check, chain, index
from adept.core.banner import print_banner

app = typer.Typer(
    add_completion=False, 
    help="Adept - The AI Engineer's Workflow Orchestrator"
)


@app.callback(invoke_without_command=True)
def _root_callback(ctx: typer.Context) -> None:
    print_banner()
    if ctx.invoked_subcommand is None:
        typer.echo(app.get_help(ctx))
        raise typer.Exit(0)

app.add_typer(write.app, name="write")
app.add_typer(check.app, name="check")
app.add_typer(chain.app, name="chain")
app.add_typer(index.app, name="index")

if __name__ == "__main__":
    app()
