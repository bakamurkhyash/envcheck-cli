import re
from pathlib import Path
from typing import Set

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False)
console = Console()


PATTERNS = [
    re.compile(r"os\.getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),   
    re.compile(r"os\.environ\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),     
    re.compile(r"os\.environ\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]")
    re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),                
    re.compile(r"process\.env\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),   
]

CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}
IGNORE_DIRS = {"node_modules", ".git", "venv", "__pycache__", ".venv", "dist", "build"}


def find_code_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in CODE_EXTENSIONS:
            if not any(part in IGNORE_DIRS for part in path.parts):
                yield path


def extract_used_vars(root: Path) -> Set[str]:
    used = set()
    for file in find_code_files(root):
        try:
            text = file.read_text(errors="ignore")
        except Exception:
            continue
        for pattern in PATTERNS:
            used.update(pattern.findall(text))
    return used


def extract_declared_vars(env_file: Path) -> Set[str]:
    declared = set()
    if not env_file.exists():
        return declared
    for line in env_file.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            if key:
                declared.add(key)
    return declared


@app.command()
def check(
    path: str = typer.Argument(".", help="Path to project root"),
    env_file: str = typer.Option(".env.example", "--env-file", "-e", help="Env file to check against"),
):
    """Scan codebase for env vars and diff against declared env file."""
    root = Path(path).resolve()
    env_path = root / env_file

    used = extract_used_vars(root)
    declared = extract_declared_vars(env_path)

    missing = sorted(used - declared)   
    unused = sorted(declared - used)   

    table = Table(title=f"envcheck: {root.name}")
    table.add_column("Variable")
    table.add_column("Status")

    for var in missing:
        table.add_row(var, "[red]MISSING (used, not declared)[/red]")
    for var in unused:
        table.add_row(var, "[yellow]UNUSED (declared, not used)[/yellow]")

    if not missing and not unused:
        console.print(f"[green]✔ All {len(used)} env vars accounted for.[/green]")
        raise typer.Exit(code=0)

    console.print(table)
    console.print(f"\nUsed in code: {len(used)}  |  Declared in {env_file}: {len(declared)}")

    if missing:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
