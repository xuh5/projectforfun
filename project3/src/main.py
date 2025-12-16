"""CLI entry point for synthetic JSON data generator."""

import sys
from pathlib import Path
from typing import Optional

import click

from .config import load_config
from .clients import OpenAIClient
from .generator import PromptBuilder
from .output import OutputHandler
from .schema import SchemaParser, SchemaValidator


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Synthetic JSON Data Generator - Generate realistic synthetic data using OpenAI."""
    pass


@cli.command()
@click.option(
    "--schema",
    "-s",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to JSON schema configuration file",
)
@click.option(
    "--count",
    "-c",
    default=1,
    type=int,
    help="Number of records to generate (default: 1)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: print to console)",
)
@click.option(
    "--model",
    "-m",
    help="OpenAI model to use (default: from config or gpt-4o-mini)",
)
@click.option(
    "--api-key",
    help="OpenAI API key (default: from OPENAI_API_KEY env var)",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate generated data against schema (default: True)",
)
@click.option(
    "--temperature",
    "-t",
    default=0.7,
    type=float,
    help="Sampling temperature (0.0 to 2.0, default: 0.7)",
)
def generate(
    schema: Path,
    count: int,
    output: Optional[Path],
    model: Optional[str],
    api_key: Optional[str],
    validate: bool,
    temperature: float,
):
    """Generate synthetic JSON data from a schema."""
    try:
        # Load configuration
        config = load_config()
        if api_key:
            config["openai_api_key"] = api_key
        if model:
            config["openai_model"] = model
        
        # Parse schema
        click.echo(f"📋 Loading schema from: {schema}")
        schema_parser = SchemaParser(str(schema))
        click.echo(f"✓ Schema loaded: {schema_parser.get_name()}")
        
        # Build prompt
        click.echo("🔨 Building generation prompt...")
        prompt_builder = PromptBuilder(schema_parser)
        prompt = prompt_builder.build_prompt(count)
        system_prompt = prompt_builder.build_system_prompt()
        
        # Initialize OpenAI client
        click.echo(f"🤖 Generating data using {config['openai_model']}...")
        client = OpenAIClient(
            api_key=config["openai_api_key"],
            model=config["openai_model"],
        )
        
        # Generate data
        generated_data = client.generate_multiple(
            prompt=prompt,
            system_prompt=system_prompt,
            count=count,
            temperature=temperature,
        )
        
        # Validate if requested
        if validate:
            click.echo("✓ Validating generated data...")
            validator = SchemaValidator(schema_parser.get_schema_dict())
            
            all_valid = True
            for i, data_item in enumerate(generated_data):
                is_valid, errors = validator.validate(data_item)
                if not is_valid:
                    all_valid = False
                    click.echo(f"⚠ Validation errors for record {i + 1}:", err=True)
                    for error in errors:
                        click.echo(f"  - {error}", err=True)
            
            if all_valid:
                click.echo("✓ All records validated successfully")
            else:
                click.echo("⚠ Some records have validation errors", err=True)
        
        # Output data
        output_handler = OutputHandler(str(output) if output else None)
        if count == 1:
            output_handler.save(generated_data[0] if generated_data else {})
        else:
            output_handler.save(generated_data)
        
        click.echo("✓ Generation complete!")
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--schema",
    "-s",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to JSON schema configuration file",
)
@click.option(
    "--data",
    "-d",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to JSON data file to validate",
)
def validate(schema: Path, data: Path):
    """Validate existing JSON data against a schema."""
    try:
        import json
        
        # Parse schema
        click.echo(f"📋 Loading schema from: {schema}")
        schema_parser = SchemaParser(str(schema))
        click.echo(f"✓ Schema loaded: {schema_parser.get_name()}")
        
        # Load data
        click.echo(f"📄 Loading data from: {data}")
        with open(data, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        
        # Validate
        validator = SchemaValidator(schema_parser.get_schema_dict())
        
        if isinstance(json_data, list):
            click.echo(f"Validating {len(json_data)} records...")
            all_valid = True
            for i, item in enumerate(json_data):
                is_valid, errors = validator.validate(item)
                if not is_valid:
                    all_valid = False
                    click.echo(f"❌ Record {i + 1} is invalid:")
                    for error in errors:
                        click.echo(f"  - {error}")
                else:
                    click.echo(f"✓ Record {i + 1} is valid")
            
            if all_valid:
                click.echo("✓ All records are valid!")
            else:
                click.echo("❌ Some records are invalid", err=True)
                sys.exit(1)
        else:
            is_valid, errors = validator.validate(json_data)
            if is_valid:
                click.echo("✓ Data is valid!")
            else:
                click.echo("❌ Data is invalid:")
                for error in errors:
                    click.echo(f"  - {error}")
                sys.exit(1)
        
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--port",
    "-p",
    default=5000,
    type=int,
    help="Port to run the web server on (default: 5000)",
)
@click.option(
    "--host",
    default="127.0.0.1",  # 改为 127.0.0.1
    help="Host to bind to (default: 127.0.0.1)",
)
def serve(port: int, host: str):
    """Start the web server for relationship generation."""
    from .web.app import app
    
    click.echo(f"🚀 Starting web server on http://{host}:{port}")
    click.echo("📝 Open your browser and navigate to the URL above")
    app.run(debug=True, host=host, port=port)


if __name__ == "__main__":
    cli()

