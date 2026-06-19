import sys
import os

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ModuleNotFoundError:
    print("HATA: CLI özellikleri için gerekli kütüphaneler eksik.")
    print("Bu özelliği kullanmak için lütfen aşağıdaki komutu çalıştırın:")
    print("    pip install 'stock-fetcher[cli]'")
    sys.exit(1)

from ..factory import ClientFactory
from ..exceptions import StockFetcherError

app = typer.Typer(help="Stock Fetcher CLI tool.")
console = Console()


@app.command()
def search(
    provider: str = typer.Argument(..., help="Provider to use (e.g., pixabay, pexels)"),
    term: str = typer.Argument(..., help="The search term (e.g., nature)"),
    limit: int = typer.Option(5, help="Number of images to fetch"),
    api_key: str = typer.Option(
        "", envvar="STOCK_FETCHER_API_KEY", help="API key for the provider"
    ),
):
    """Search for images across different providers via CLI."""
    if not api_key:
        env_var_name = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_var_name, "")

    try:
        client = ClientFactory.get(provider, api_key=api_key)
        images = client.search(term, limit=limit)

        if not images:
            console.print(
                f"[yellow]No images found for '{term}' on {provider}.[/yellow]"
            )
            return

        table = Table(title=f"Results for '{term}' from {provider.capitalize()}")
        table.add_column("ID", style="cyan")
        table.add_column("URL", style="green", overflow="fold")

        for img in images:
            table.add_row(str(img.get("id", "N/A")), img.get("url", "N/A"))

        console.print(table)

    except StockFetcherError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
