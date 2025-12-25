#!/usr/bin/env python3
"""CLI utility for managing secrets."""

import sys
import json
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from pulsepilot.core.secrets import (
    get_secrets_manager,
    SecretsManagerFactory,
    SecretProvider,
)
from pulsepilot.core.oauth import InstagramOAuthManager, FacebookOAuthManager, GoogleOAuthManager, OAuthToken
from pulsepilot.core.key_rotation import KeyRotationManager, get_validator

app = typer.Typer(help="Manage secrets and OAuth tokens for PulsePilot")
console = Console()


@app.command()
def get(
    secret_name: str = typer.Argument(..., help="Name of the secret to retrieve"),
    show_value: bool = typer.Option(False, "--show", help="Show the secret value"),
):
    """Get a secret value."""
    try:
        sm = get_secrets_manager()
        value = sm.get_secret(secret_name)

        if value:
            if show_value:
                console.print(f"[green]✓[/green] {secret_name}: {value}")
            else:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                console.print(f"[green]✓[/green] {secret_name}: {masked}")
                console.print("[dim]Use --show to display full value[/dim]")
        else:
            console.print(f"[red]✗[/red] Secret '{secret_name}' not found")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def set(
    secret_name: str = typer.Argument(..., help="Name of the secret to set"),
    secret_value: Optional[str] = typer.Option(None, "--value", help="Secret value"),
):
    """Set a secret value."""
    try:
        # Prompt for value if not provided
        if secret_value is None:
            secret_value = Prompt.ask(f"Enter value for {secret_name}", password=True)

        sm = get_secrets_manager()
        success = sm.set_secret(secret_name, secret_value)

        if success:
            console.print(f"[green]✓[/green] Secret '{secret_name}' set successfully")
        else:
            console.print(f"[red]✗[/red] Failed to set secret '{secret_name}'")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def delete(
    secret_name: str = typer.Argument(..., help="Name of the secret to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a secret."""
    try:
        if not force:
            confirm = Confirm.ask(f"Delete secret '{secret_name}'?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        sm = get_secrets_manager()
        success = sm.delete_secret(secret_name)

        if success:
            console.print(f"[green]✓[/green] Secret '{secret_name}' deleted")
        else:
            console.print(f"[red]✗[/red] Failed to delete secret '{secret_name}'")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def rotate(
    secret_name: str = typer.Argument(..., help="Name of the secret to rotate"),
    new_value: Optional[str] = typer.Option(None, "--value", help="New secret value"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Validate new key"),
):
    """Rotate a secret with validation and rollback."""
    try:
        # Prompt for new value if not provided
        if new_value is None:
            new_value = Prompt.ask(f"Enter new value for {secret_name}", password=True)

        # Get validator if validation enabled
        validator = get_validator(secret_name) if validate else None

        # Perform rotation
        rotation_mgr = KeyRotationManager()
        with console.status(f"[bold blue]Rotating {secret_name}..."):
            record = rotation_mgr.rotate_key(
                secret_name=secret_name,
                new_value=new_value,
                validator=validator,
                auto_rollback=True
            )

        # Display result
        if record.status.value == "completed":
            console.print(f"[green]✓[/green] Successfully rotated '{secret_name}'")
            console.print(f"[dim]Timestamp: {record.timestamp}[/dim]")
        elif record.status.value == "rolled_back":
            console.print(f"[yellow]⚠[/yellow] Rotation failed, rolled back to previous value")
            console.print(f"[dim]Error: {record.error_message}[/dim]")
        else:
            console.print(f"[red]✗[/red] Rotation failed: {record.error_message}")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def oauth_set(
    platform: str = typer.Argument(..., help="Platform: instagram, facebook, or google"),
    access_token: str = typer.Option(..., "--access-token", help="OAuth access token"),
    refresh_token: Optional[str] = typer.Option(None, "--refresh-token", help="OAuth refresh token"),
    expires_in: int = typer.Option(3600, "--expires-in", help="Token expiration in seconds"),
):
    """Set OAuth token for a platform."""
    try:
        platform = platform.lower()

        # Create token object
        token = OAuthToken(
            access_token=access_token,
            refresh_token=refresh_token or access_token,
            expires_in=expires_in,
            token_type="Bearer"
        )

        # Store token based on platform
        if platform == "instagram":
            mgr = InstagramOAuthManager()
            mgr.set_token(token)
            console.print(f"[green]✓[/green] Instagram OAuth token set")
            console.print("[dim]Don't forget to set INSTAGRAM_IG_USER_ID[/dim]")

        elif platform == "facebook":
            mgr = FacebookOAuthManager()
            mgr.set_token(token)
            console.print(f"[green]✓[/green] Facebook OAuth token set")
            console.print("[dim]Don't forget to set FACEBOOK_PAGE_ID[/dim]")

        elif platform == "google":
            mgr = GoogleOAuthManager()
            mgr.set_token(token)
            console.print(f"[green]✓[/green] Google OAuth token set")

        else:
            console.print(f"[red]✗[/red] Unknown platform: {platform}")
            console.print("[dim]Supported: instagram, facebook, google[/dim]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def oauth_get(
    platform: str = typer.Argument(..., help="Platform: instagram, facebook, or google"),
):
    """Get OAuth token for a platform."""
    try:
        platform = platform.lower()

        # Get token based on platform
        if platform == "instagram":
            mgr = InstagramOAuthManager()
        elif platform == "facebook":
            mgr = FacebookOAuthManager()
        elif platform == "google":
            mgr = GoogleOAuthManager()
        else:
            console.print(f"[red]✗[/red] Unknown platform: {platform}")
            sys.exit(1)

        token = mgr.get_token()

        if token:
            table = Table(title=f"{platform.title()} OAuth Token")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Access Token", token.access_token[:20] + "...")
            table.add_row("Type", token.token_type)
            table.add_row("Expires In", f"{token.expires_in}s")
            table.add_row("Expires At", str(token.expires_at))
            table.add_row("Is Expired", "❌ Yes" if token.is_expired else "✓ No")

            if token.refresh_token and token.refresh_token != token.access_token:
                table.add_row("Refresh Token", token.refresh_token[:20] + "...")

            console.print(table)
        else:
            console.print(f"[yellow]⚠[/yellow] No OAuth token found for {platform}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def oauth_refresh(
    platform: str = typer.Argument(..., help="Platform: instagram, facebook, or google"),
):
    """Manually refresh OAuth token."""
    try:
        platform = platform.lower()

        # Get manager based on platform
        if platform == "instagram":
            mgr = InstagramOAuthManager()
        elif platform == "facebook":
            mgr = FacebookOAuthManager()
        elif platform == "google":
            mgr = GoogleOAuthManager()
        else:
            console.print(f"[red]✗[/red] Unknown platform: {platform}")
            sys.exit(1)

        with console.status(f"[bold blue]Refreshing {platform} token..."):
            token = mgr.get_token(force_refresh=True)

        if token:
            console.print(f"[green]✓[/green] Token refreshed successfully")
            console.print(f"[dim]New expiration: {token.expires_at}[/dim]")
        else:
            console.print(f"[red]✗[/red] Failed to refresh token")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def migrate(
    from_provider: str = typer.Option("env", "--from", help="Source provider"),
    to_provider: str = typer.Option("aws", "--to", help="Destination provider"),
    secrets: str = typer.Option(..., "--secrets", help="Comma-separated list of secret names"),
):
    """Migrate secrets between providers."""
    try:
        # Parse secret names
        secret_names = [s.strip() for s in secrets.split(",")]

        # Create source and destination managers
        from_sm = SecretsManagerFactory.create(SecretProvider(from_provider))
        to_sm = SecretsManagerFactory.create(SecretProvider(to_provider))

        console.print(f"[bold]Migrating {len(secret_names)} secrets")
        console.print(f"From: {from_provider}")
        console.print(f"To: {to_provider}\n")

        # Migrate each secret
        success_count = 0
        for secret_name in secret_names:
            with console.status(f"Migrating {secret_name}..."):
                value = from_sm.get_secret(secret_name)
                if value:
                    if to_sm.set_secret(secret_name, value):
                        console.print(f"[green]✓[/green] {secret_name}")
                        success_count += 1
                    else:
                        console.print(f"[red]✗[/red] {secret_name} (write failed)")
                else:
                    console.print(f"[yellow]⊘[/yellow] {secret_name} (not found)")

        console.print(f"\n[bold green]Migrated {success_count}/{len(secret_names)} secrets[/bold green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def info():
    """Show current secrets manager configuration."""
    try:
        sm = get_secrets_manager()

        table = Table(title="Secrets Manager Configuration")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Provider", type(sm).__name__)
        table.add_row("Type", sm.__class__.__module__)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
