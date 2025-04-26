"""
Command-line interface for ErrorTrace Pro
"""
import os
import sys
import logging
import traceback
import json
import importlib
from importlib.machinery import SourceFileLoader

try:
    import click
except ImportError:
    click = None
    
from .handler import ExceptionHandler
from .solutions import SolutionProvider
from .cloud_logger import CloudLogger

logger = logging.getLogger(__name__)

# Check if click is available, otherwise define a basic CLI
if click:
    @click.group()
    @click.version_option()
    def cli():
        """ErrorTrace Pro - Enhanced Exception Handling for Python"""
        pass
    
    @cli.command()
    @click.argument('script', type=click.Path(exists=True))
    @click.option('--cloud', is_flag=True, help='Enable cloud logging')
    @click.option('--provider', type=click.Choice(['http', 'gcp', 'aws', 'azure']),
                  default='http', help='Cloud logging provider')
    @click.option('--endpoint', help='HTTP endpoint for logging')
    @click.option('--api-key', help='API key for cloud provider')
    @click.option('--project-id', help='Project ID (for GCP)')
    @click.option('--solutions', type=click.Path(exists=True), help='Custom solutions JSON file')
    @click.option('--no-color', is_flag=True, help='Disable colored output')
    def run(script, cloud, provider, endpoint, api_key, project_id, solutions, no_color):
        """Run a Python script with ErrorTrace Pro error handling"""
        # Set up the environment variables for cloud logging
        if cloud:
            os.environ["ERRORTRACE_PROVIDER"] = provider
            if endpoint:
                os.environ["ERRORTRACE_ENDPOINT"] = endpoint
            if api_key:
                os.environ["ERRORTRACE_API_KEY"] = api_key
            if project_id:
                os.environ["ERRORTRACE_PROJECT_ID"] = project_id
        
        # Create the exception handler
        handler = ExceptionHandler(
            solutions_path=solutions,
            cloud_logging=cloud,
            cloud_provider=provider,
            api_key=api_key,
            project_id=project_id,
            colored_output=not no_color
        )
        
        # Set up exception hook
        def exception_hook(exc_type, exc_value, exc_traceback):
            handler.handle(exc_type, exc_value, exc_traceback)
            # Don't call the original hook as we'll exit after this
        
        sys.excepthook = exception_hook
        
        # Run the script
        try:
            # Get the directory containing the script
            script_dir = os.path.dirname(os.path.abspath(script))
            
            # Add the script directory to the path so imports work
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            # Load the script as a module
            module_name = os.path.basename(script).replace('.py', '')
            module = SourceFileLoader(module_name, script).load_module()
            
            # Exit with the same code as the script
            sys.exit(0)
        except SystemExit as e:
            # Pass through system exit codes
            sys.exit(e.code)
        except Exception:
            # The exception hook will handle the error display
            sys.exit(1)
    
    @cli.command()
    @click.option('--output', type=click.Path(), help='Output file path (default: stdout)')
    def init_solutions(output):
        """Generate a template solutions database file"""
        provider = SolutionProvider()
        solutions = provider._get_default_solutions()
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(solutions, f, indent=2)
            click.echo(f"Solutions database written to {output}")
        else:
            click.echo(json.dumps(solutions, indent=2))
    
    def main():
        """Main entry point for the CLI"""
        cli()
    
else:
    # Simple CLI if click is not available
    def main():
        """Basic CLI entry point without click"""
        args = sys.argv[1:]
        
        if not args or args[0] in ['-h', '--help']:
            print("ErrorTrace Pro - Enhanced Exception Handling for Python")
            print("Usage: errortrace run <script> [options]")
            print("       errortrace init-solutions [--output FILE]")
            print("\nOptions:")
            print("  --cloud                  Enable cloud logging")
            print("  --provider=PROVIDER      Cloud provider (http, gcp, aws, azure)")
            print("  --endpoint=ENDPOINT      HTTP endpoint for logging")
            print("  --api-key=KEY            API key for cloud provider")
            print("  --project-id=ID          Project ID (for GCP)")
            print("  --solutions=FILE         Custom solutions JSON file")
            print("  --no-color               Disable colored output")
            return
            
        if args[0] == 'run' and len(args) > 1:
            script = args[1]
            if not os.path.exists(script):
                print(f"Error: Script '{script}' not found")
                sys.exit(1)
                
            # Parse options
            cloud = '--cloud' in args
            provider = 'http'
            endpoint = None
            api_key = None
            project_id = None
            solutions = None
            no_color = '--no-color' in args
            
            for arg in args[2:]:
                if arg.startswith('--provider='):
                    provider = arg.split('=')[1]
                elif arg.startswith('--endpoint='):
                    endpoint = arg.split('=')[1]
                elif arg.startswith('--api-key='):
                    api_key = arg.split('=')[1]
                elif arg.startswith('--project-id='):
                    project_id = arg.split('=')[1]
                elif arg.startswith('--solutions='):
                    solutions = arg.split('=')[1]
            
            # Set up the environment variables for cloud logging
            if cloud:
                os.environ["ERRORTRACE_PROVIDER"] = provider
                if endpoint:
                    os.environ["ERRORTRACE_ENDPOINT"] = endpoint
                if api_key:
                    os.environ["ERRORTRACE_API_KEY"] = api_key
                if project_id:
                    os.environ["ERRORTRACE_PROJECT_ID"] = project_id
            
            # Create the exception handler
            handler = ExceptionHandler(
                solutions_path=solutions,
                cloud_logging=cloud,
                cloud_provider=provider,
                api_key=api_key,
                project_id=project_id,
                colored_output=not no_color
            )
            
            # Set up exception hook
            def exception_hook(exc_type, exc_value, exc_traceback):
                handler.handle(exc_type, exc_value, exc_traceback)
                # Don't call the original hook as we'll exit after this
            
            sys.excepthook = exception_hook
            
            # Run the script
            try:
                # Get the directory containing the script
                script_dir = os.path.dirname(os.path.abspath(script))
                
                # Add the script directory to the path so imports work
                if script_dir not in sys.path:
                    sys.path.insert(0, script_dir)
                
                # Load the script as a module
                module_name = os.path.basename(script).replace('.py', '')
                module = SourceFileLoader(module_name, script).load_module()
                
                # Exit with the same code as the script
                sys.exit(0)
            except SystemExit as e:
                # Pass through system exit codes
                sys.exit(e.code)
            except Exception:
                # The exception hook will handle the error display
                sys.exit(1)
        
        elif args[0] == 'init-solutions':
            provider = SolutionProvider()
            solutions = provider._get_default_solutions()
            
            output = None
            for arg in args[1:]:
                if arg.startswith('--output='):
                    output = arg.split('=')[1]
            
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(solutions, f, indent=2)
                print(f"Solutions database written to {output}")
            else:
                print(json.dumps(solutions, indent=2))
        
        else:
            print("Error: Unknown command or missing required argument")
            print("Use 'errortrace --help' for usage information")
            sys.exit(1)

if __name__ == "__main__":
    main()
