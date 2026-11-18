import sys
import os
import json
import csv
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
import requests

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
    )
except ModuleNotFoundError:
    print("Error: Required CLI dependencies ('typer', 'rich') are missing.", file=sys.stderr)
    print("Install the CLI extras by running:", file=sys.stderr)
    print("    pip install 'stock-fetcher[cli]'", file=sys.stderr)
    sys.exit(1)

from ..factory import ClientFactory
from ..exceptions import StockFetcherError, AuthenticationError, ProviderNotFoundError

__version__ = "0.2.0"
MAX_DOWNLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB per image ceiling

app = typer.Typer(
    name="stock-fetcher",
    help="CLI utility for searching and downloading copyright-free stock photos.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)

PROVIDER_ENV_MAP: Dict[str, Optional[str]] = {
    "pixabay": "PIXABAY_API_KEY",
    "pexels": "PEXELS_API_KEY",
    "unsplash": "UNSPLASH_API_KEY",
    "flickr": None,
}


def _resolve_api_key(provider: str, explicit_key: str = "") -> str:
    """Resolve API key from explicit option, provider env var, or global env var."""
    if explicit_key:
        return explicit_key.strip()
    env_var = PROVIDER_ENV_MAP.get(provider.lower())
    if env_var:
        val = os.getenv(env_var, "")
        if val:
            return val.strip()
    return os.getenv("STOCK_FETCHER_API_KEY", "").strip()


def _download_single_image(
    url: str,
    output_dir: str,
    filename: Optional[str] = None,
    progress: Optional[Progress] = None,
    task_id: Optional[Any] = None,
) -> str:
    """Download an image from a URL to disk with streaming, size bounds, and path traversal defense."""
    # 1. Scheme and Host Validation
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Disallowed protocol scheme: '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")
    if not parsed.netloc:
        raise ValueError("Invalid URL: missing host authority.")

    # 2. Strict Filename Sanitization & Directory Traversal Defense
    os.makedirs(output_dir, exist_ok=True)
    canonical_dir = os.path.realpath(os.path.abspath(output_dir))

    raw_name = filename if filename else os.path.basename(parsed.path)
    # Strip any directory separators, null bytes, and traversal components
    safe_name = os.path.basename(raw_name).replace("\\", "").replace("/", "").replace("\0", "").strip()

    if not safe_name or safe_name in (".", "..") or "." not in safe_name:
        safe_name = f"image_{abs(hash(url)) % 100000000}.jpg"

    dest_path = os.path.join(canonical_dir, safe_name)
    canonical_dest = os.path.realpath(os.path.abspath(dest_path))

    # Boundary check: ensure target stays strictly within canonical_dir
    if not (canonical_dest == canonical_dir or canonical_dest.startswith(canonical_dir + os.sep)):
        raise ValueError(f"Path traversal violation detected for destination: {filename}")

    # 3. Request Execution with Size Guard
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    # Verify Content-Length header if reported
    content_length = int(response.headers.get("content-length", 0))
    if content_length > MAX_DOWNLOAD_SIZE_BYTES:
        raise ValueError(
            f"Image size exceeds maximum permitted limit ({content_length} > {MAX_DOWNLOAD_SIZE_BYTES} bytes)."
        )

    if progress and task_id is not None and content_length > 0:
        progress.update(task_id, total=content_length)

    downloaded = 0
    try:
        with open(canonical_dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=16384):
                if chunk:
                    downloaded += len(chunk)
                    if downloaded > MAX_DOWNLOAD_SIZE_BYTES:
                        raise ValueError(
                            f"Downloaded content exceeded {MAX_DOWNLOAD_SIZE_BYTES // (1024 * 1024)} MB limit."
                        )
                    f.write(chunk)
                    if progress and task_id is not None:
                        progress.update(task_id, advance=len(chunk))
    except Exception:
        # Clean up partial artifact on download failure
        if os.path.exists(canonical_dest):
            try:
                os.remove(canonical_dest)
            except OSError:
                pass
        raise

    return canonical_dest


def _execute_search(
    provider_name: str,
    term: str,
    limit: int,
    explicit_key: str = "",
) -> List[Dict[str, Any]]:
    """Execute search against a single provider."""
    api_key = _resolve_api_key(provider_name, explicit_key)
    client = ClientFactory.get(provider_name, api_key=api_key)
    raw_results = client.search(term, limit=limit)

    normalized: List[Dict[str, Any]] = []
    for item in raw_results:
        normalized.append({
            "id": str(item.get("id", "N/A")),
            "source": str(item.get("source", provider_name)),
            "url_page": item.get("url") or item.get("url_page") or "N/A",
            "url_original": item.get("url_original") or item.get("url") or "N/A",
            "title": item.get("title") or item.get("description") or "",
        })
    return normalized


def _render_output(
    results: List[Dict[str, Any]],
    format_type: str,
    term: str,
    provider_label: str,
) -> None:
    """Render search results in the requested format."""
    format_lower = format_type.lower()

    if format_lower == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if format_lower == "urls":
        for item in results:
            target_url = item.get("url_original")
            if target_url and target_url != "N/A":
                print(target_url)
            else:
                print(item.get("url_page", ""))
        return

    if format_lower == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(["id", "source", "url_page", "url_original", "title"])
        for item in results:
            writer.writerow([
                item.get("id", ""),
                item.get("source", ""),
                item.get("url_page", ""),
                item.get("url_original", ""),
                item.get("title", ""),
            ])
        return

    # Default: Rich Table
    table = Table(
        title=f"Results for '{term}' [{provider_label}]",
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Source", style="bold cyan", width=10)
    table.add_column("ID", style="green", width=14)
    table.add_column("Webpage", style="blue", overflow="fold")
    table.add_column("Direct Image URL", style="white", overflow="fold")

    for idx, item in enumerate(results, start=1):
        table.add_row(
            str(idx),
            item.get("source", "").upper(),
            item.get("id", ""),
            item.get("url_page", ""),
            item.get("url_original", ""),
        )

    console.print(table)
    console.print(f"[dim]Total records: {len(results)}[/dim]\n")


def _batch_download(results: List[Dict[str, Any]], output_dir: str) -> None:
    """Download all images from search results with a progress bar."""
    valid_items = [
        item for item in results
        if item.get("url_original") and item.get("url_original") != "N/A"
    ]
    if not valid_items:
        console.print("[yellow]No direct download URLs found in results.[/yellow]")
        return

    console.print(f"Downloading [bold cyan]{len(valid_items)}[/bold cyan] images to [bold]{output_dir}[/bold]...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        overall = progress.add_task("Total download progress", total=len(valid_items))

        for item in valid_items:
            url = item["url_original"]
            src = item.get("source", "stock")
            img_id = item.get("id", "item")
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1] or ".jpg"
            filename = f"{src}_{img_id}{ext}"

            try:
                _download_single_image(url, output_dir=output_dir, filename=filename)
            except Exception as exc:
                err_console.print(f"[red]Failed to download {url}: {exc}[/red]")
            finally:
                progress.advance(overall)

    console.print(f"[green]Download completed. Files saved to [bold]{output_dir}[/bold][/green]")


@app.command(name="search")
def search(
    provider: str = typer.Argument(
        ...,
        help="Target provider: 'pixabay', 'pexels', 'unsplash', 'flickr', or 'all'.",
    ),
    term: str = typer.Argument(
        ...,
        help="Search query term (e.g. 'nature', 'cyberpunk city').",
    ),
    limit: int = typer.Option(
        5,
        "--limit",
        "-l",
        help="Maximum number of images to fetch per provider.",
        min=1,
        max=100,
    ),
    api_key: str = typer.Option(
        "",
        "--api-key",
        "-k",
        help="Explicit API key. Overrides environment variables.",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: 'table', 'json', 'csv', or 'urls'.",
    ),
    download: bool = typer.Option(
        False,
        "--download",
        "-d",
        help="Automatically download fetched images.",
    ),
    output_dir: str = typer.Option(
        "./downloads",
        "--output-dir",
        "-o",
        help="Destination directory when downloading images.",
    ),
) -> None:
    """Search for copyright-free stock photos across providers."""
    provider_clean = provider.strip().lower()
    results: List[Dict[str, Any]] = []
    skipped_providers: List[str] = []

    if provider_clean == "all":
        available = list(ClientFactory._clients.keys())
        for p in available:
            try:
                p_results = _execute_search(p, term, limit, api_key)
                results.extend(p_results)
            except AuthenticationError:
                skipped_providers.append(f"{p} (API key missing)")
            except Exception as exc:
                skipped_providers.append(f"{p} ({exc})")

        if not results:
            err_console.print(f"[yellow]No images retrieved for '{term}' from any provider.[/yellow]")
            if skipped_providers:
                err_console.print(f"[dim]Skipped providers: {', '.join(skipped_providers)}[/dim]")
            raise typer.Exit(code=0)

        label = "All Providers"
    else:
        try:
            results = _execute_search(provider_clean, term, limit, api_key)
        except AuthenticationError as e:
            env_var = PROVIDER_ENV_MAP.get(provider_clean, f"{provider_clean.upper()}_API_KEY")
            err_console.print(f"[red]Authentication Error:[/red] {e}")
            if env_var:
                err_console.print(f"[yellow]Tip:[/yellow] Set the [bold]{env_var}[/bold] environment variable or pass [bold]--api-key[/bold].")
            raise typer.Exit(code=1)
        except ProviderNotFoundError as e:
            err_console.print(f"[red]Error:[/red] {e}")
            err_console.print(f"[yellow]Available providers:[/yellow] {', '.join(ClientFactory._clients.keys())}, all")
            raise typer.Exit(code=1)
        except StockFetcherError as e:
            err_console.print(f"[red]Fetch Error:[/red] {e}")
            raise typer.Exit(code=1)
        except ValueError as e:
            err_console.print(f"[red]Validation Error:[/red] {e}")
            raise typer.Exit(code=1)

        label = provider_clean.capitalize()

    if not results:
        console.print(f"[yellow]No images found for '{term}' on {label}.[/yellow]")
        return

    _render_output(results, format, term, label)

    if skipped_providers and format == "table":
        console.print(f"[dim]Notice: Skipped providers: {', '.join(skipped_providers)}[/dim]\n")

    if download:
        _batch_download(results, output_dir)


@app.command(name="find")
def find(
    term: str = typer.Argument(
        ...,
        help="Search query term across all available providers.",
    ),
    limit: int = typer.Option(
        5,
        "--limit",
        "-l",
        help="Maximum images per provider.",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: 'table', 'json', 'csv', or 'urls'.",
    ),
    download: bool = typer.Option(
        False,
        "--download",
        "-d",
        help="Automatically download fetched images.",
    ),
    output_dir: str = typer.Option(
        "./downloads",
        "--output-dir",
        "-o",
        help="Destination directory when downloading images.",
    ),
) -> None:
    """Convenient shortcut to search all providers simultaneously."""
    search(
        provider="all",
        term=term,
        limit=limit,
        api_key="",
        format=format,
        download=download,
        output_dir=output_dir,
    )


@app.command(name="download")
def download_cmd(
    url: str = typer.Argument(
        ...,
        help="Direct URL of the image to download.",
    ),
    output_dir: str = typer.Option(
        "./downloads",
        "--output-dir",
        "-o",
        help="Destination directory.",
    ),
    filename: Optional[str] = typer.Option(
        None,
        "--filename",
        "-n",
        help="Custom output filename. Defaults to URL basename.",
    ),
) -> None:
    """Download a single image from a direct URL to disk."""
    console.print(f"Downloading from [cyan]{url}[/cyan]...")
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading image", total=None)
            saved_path = _download_single_image(
                url=url,
                output_dir=output_dir,
                filename=filename,
                progress=progress,
                task_id=task,
            )
        file_size = os.path.getsize(saved_path)
        console.print(f"[green]Saved successfully:[/green] [bold]{saved_path}[/bold] ({file_size / 1024:.1f} KB)")
    except Exception as exc:
        err_console.print(f"[red]Download failed:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command(name="providers")
def list_providers() -> None:
    """List all supported providers, auth requirements, and current configuration status."""
    table = Table(
        title="Stock Fetcher Supported Providers",
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Provider", style="bold cyan", width=12)
    table.add_column("Access Mode", width=14)
    table.add_column("Auth Required", width=14)
    table.add_column("Environment Variable", style="blue", width=22)
    table.add_column("Status", width=18)

    for p in ClientFactory._clients.keys():
        env_var = PROVIDER_ENV_MAP.get(p)
        if env_var is None:
            auth_req = "No"
            env_display = "None"
            status = "[green]Ready (No Key Required)[/green]"
        else:
            auth_req = "Yes"
            env_display = env_var
            val = os.getenv(env_var) or os.getenv("STOCK_FETCHER_API_KEY")
            if val:
                status = "[green]Configured[/green]"
            else:
                status = "[yellow]Key Missing[/yellow]"

        mode = "HTML Scraper" if p == "flickr" else "REST API"
        table.add_row(p, mode, auth_req, env_display, status)

    console.print(table)


@app.command(name="keys")
def check_keys() -> None:
    """Check provider API credential status in the current environment."""
    table = Table(title="Environment API Key Status", header_style="bold magenta")
    table.add_column("Provider", style="bold cyan")
    table.add_column("Variable", style="blue")
    table.add_column("Status")

    for p, env_var in PROVIDER_ENV_MAP.items():
        if env_var is None:
            table.add_row(p, "-", "[dim]Not Required[/dim]")
        else:
            val = os.getenv(env_var) or os.getenv("STOCK_FETCHER_API_KEY")
            if val:
                masked = val[:4] + "..." + val[-2:] if len(val) > 6 else "***"
                table.add_row(p, env_var, f"[green]Configured ({masked})[/green]")
            else:
                table.add_row(p, env_var, "[red]Not Set[/red]")

    console.print(table)


@app.command(name="version")
def version_cmd() -> None:
    """Display stock-fetcher version and runtime details."""
    console.print(Panel(
        f"[bold cyan]stock-fetcher[/bold cyan] version [bold green]{__version__}[/bold green]\n"
        f"Python: {sys.version.split()[0]} ({sys.platform})\n"
        f"Available Providers: {', '.join(ClientFactory._clients.keys())}",
        title="Package Info",
        expand=False,
    ))


if __name__ == "__main__":
    app()
