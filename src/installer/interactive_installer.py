import os
import sys
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any

import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.installer.questionnaire import (
    get_authelia_questions,
    get_searxng_questions,
    get_swag_questions,
    get_synapse_questions,
)
from src.installer.configurator import update_config_file, backup_file

console = Console()

CONFIG_PATHS = {
    "Authelia": [
        "config/authelia/configuration.yml",
        "config/authelia/users_database.yml",
    ],
    "Searxng": [
        "config/searxng/settings.yml",
    ],
    "SWAG": [
        "config/swag/nginx/authelia-location.conf",
        "config/swag/nginx/proxy-confs/authelia.subdomain.conf",
        "config/swag/nginx/proxy-confs/matrix.subdomain.conf",
        "config/swag/nginx/proxy-confs/search.subdomain.conf",
        "config/swag/nginx/proxy-confs/searxng.subdomain.conf",
    ],
    "Synapse": [
        "config/synapse/homeserver.yaml",
    ],
}

class Installer:
    def __init__(self):
        self.changes: Dict[str, Dict[str, Any]] = {
            "Authelia": {},
            "Searxng": {},
            "SWAG": {},
            "Synapse": {},
        }
        self.config_data: Dict[str, Dict[str, Any]] = {}

    def check_files_exist(self) -> bool:
        missing_files = []
        for service, paths in CONFIG_PATHS.items():
            for path in paths:
                if not Path(path).exists():
                    missing_files.append(path)
        if missing_files:
            console.print("[bold red]Error: The following configuration files are missing:[/bold red]")
            for f in missing_files:
                console.print(f" - {f}")
            return False
        return True

    def load_configs(self):
        for service, paths in CONFIG_PATHS.items():
            self.config_data[service] = {}
            for path in paths:
                try:
                    with open(path, "r") as f:
                        if path.endswith(".yml") or path.endswith(".yaml"):
                            data = yaml.safe_load(f) or {}
                        else:
                            # For conf files, just read as text
                            data = f.read()
                        self.config_data[service][path] = data
                except Exception as e:
                    console.print(f"[red]Failed to load {path}: {e}[/red]")
                    sys.exit(1)

    def run(self):
        console.clear()
        console.print(Panel(Text("Interactive Installer for Services", justify="center", style="bold white on black"), expand=False))
        if not self.check_files_exist():
            console.print("[red]Please ensure all configuration files exist before running the installer.[/red]")
            sys.exit(1)
        self.load_configs()

        while True:
            choice = questionary.select(
                "Select a service to configure:",
                choices=[
                    "Configure Authelia",
                    "Configure Searxng",
                    "Configure SWAG",
                    "Configure Synapse",
                    "View Summary / Preview Changes",
                    "Save & Exit",
                    "Exit Without Saving",
                ],
            ).ask()

            if choice == "Configure Authelia":
                self.configure_authelia()
            elif choice == "Configure Searxng":
                self.configure_searxng()
            elif choice == "Configure SWAG":
                self.configure_swag()
            elif choice == "Configure Synapse":
                self.configure_synapse()
            elif choice == "View Summary / Preview Changes":
                self.preview_changes()
            elif choice == "Save & Exit":
                self.save_changes()
                console.print("[green]All changes saved. Exiting installer.[/green]")
                break
            elif choice == "Exit Without Saving":
                console.print("[yellow]Exiting without saving changes.[/yellow]")
                break

    def configure_authelia(self):
        console.print(Panel("[bold]Configuring Authelia[/bold]", style="cyan"))
        questions = get_authelia_questions(self.config_data.get("Authelia", {}))
        answers = {}
        for q in questions:
            answer = questionary.text(q["message"], default=q.get("default", "")).ask()
            answers[q["key"]] = answer
        self.changes["Authelia"].update(answers)
        console.print("[green]Authelia configuration updated in memory.[/green]")

    def configure_searxng(self):
        console.print(Panel("[bold]Configuring Searxng[/bold]", style="cyan"))
        questions = get_searxng_questions(self.config_data.get("Searxng", {}))
        answers = {}
        for q in questions:
            answer = questionary.text(q["message"], default=q.get("default", "")).ask()
            answers[q["key"]] = answer
        self.changes["Searxng"].update(answers)
        console.print("[green]Searxng configuration updated in memory.[/green]")

    def configure_swag(self):
        console.print(Panel("[bold]Configuring SWAG[/bold]", style="cyan"))
        questions = get_swag_questions(self.config_data.get("SWAG", {}))
        answers = {}
        for q in questions:
            answer = questionary.text(q["message"], default=q.get("default", "")).ask()
            answers[q["key"]] = answer
        self.changes["SWAG"].update(answers)
        console.print("[green]SWAG configuration updated in memory.[/green]")

    def configure_synapse(self):
        console.print(Panel("[bold]Configuring Synapse[/bold]", style="cyan"))
        questions = get_synapse_questions(self.config_data.get("Synapse", {}))
        answers = {}
        for q in questions:
            answer = questionary.text(q["message"], default=q.get("default", "")).ask()
            answers[q["key"]] = answer
        self.changes["Synapse"].update(answers)
        console.print("[green]Synapse configuration updated in memory.[/green]")

    def preview_changes(self):
        console.print(Panel("[bold]Preview of Changes to be Saved[/bold]", style="magenta"))
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Service")
        table.add_column("Key")
        table.add_column("Value")
        for service, changes in self.changes.items():
            if changes:
                for key, value in changes.items():
                    table.add_row(service, key, str(value))
        if not any(self.changes.values()):
            console.print("[yellow]No changes made yet.[/yellow]")
        else:
            console.print(table)

    def save_changes(self):
        from src.installer.configurator import backup_file
        import yaml

        for service, changes in self.changes.items():
            if not changes:
                continue
            for path in CONFIG_PATHS[service]:
                # Only update YAML files here; skip conf files for now
                if path.endswith(".yml") or path.endswith(".yaml"):
                    try:
                        backup_file(path)
                        with open(path, "r") as f:
                            data = yaml.safe_load(f) or {}
                        # Update data with changes (simple flat update)
                        data.update(changes)
                        with open(path, "w") as f:
                            yaml.safe_dump(data, f)
                        console.print(f"[green]Updated {path}[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to update {path}: {e}[/red]")
                else:
                    # For conf files, skipping update in this version
                    console.print(f"[yellow]Skipping update for non-YAML file {path}[/yellow]")

def main():
    installer = Installer()
    installer.run()

if __name__ == "__main__":
    main()
