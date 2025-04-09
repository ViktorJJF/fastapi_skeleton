#!/usr/bin/env python3
"""
Verify the migration setup.
This script checks if the migration setup is correctly configured.
"""

import os
import sys
import importlib.util
from pathlib import Path
import colorama
from colorama import Fore, Style


def check_file_exists(file_path, message):
    """Check if a file exists and print an appropriate message."""
    exists = os.path.isfile(file_path)
    status = f"{Fore.GREEN}✓" if exists else f"{Fore.RED}✗"
    print(f"{status} {message}{Style.RESET_ALL}")
    return exists


def check_directory_exists(dir_path, message):
    """Check if a directory exists and print an appropriate message."""
    exists = os.path.isdir(dir_path)
    status = f"{Fore.GREEN}✓" if exists else f"{Fore.RED}✗"
    print(f"{status} {message}{Style.RESET_ALL}")
    return exists


def check_import(module_path, expected_attributes):
    """Check if a module can be imported and contains expected attributes."""
    try:
        spec = importlib.util.spec_from_file_location("module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        missing = [attr for attr in expected_attributes if not hasattr(module, attr)]
        if missing:
            print(f"{Fore.RED}✗ Module {module_path} is missing attributes: {', '.join(missing)}{Style.RESET_ALL}")
            return False
        else:
            print(f"{Fore.GREEN}✓ Module {module_path} contains all required attributes{Style.RESET_ALL}")
            return True
    except Exception as e:
        print(f"{Fore.RED}✗ Error importing {module_path}: {str(e)}{Style.RESET_ALL}")
        return False


def check_alembic_cmd():
    """Check if alembic command is available."""
    try:
        import subprocess
        result = subprocess.run(["alembic", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"{Fore.GREEN}✓ Alembic is installed: {version}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}✗ Alembic command failed: {result.stderr}{Style.RESET_ALL}")
            return False
    except FileNotFoundError:
        print(f"{Fore.RED}✗ Alembic command not found in PATH{Style.RESET_ALL}")
        return False


def main():
    """Main function to verify migration setup."""
    # Initialize colorama
    colorama.init()
    
    print(f"{Fore.BLUE}Verifying migration setup...{Style.RESET_ALL}")
    
    # Set the working directory to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = True
    
    # Check for alembic command
    success &= check_alembic_cmd()
    
    # Check for essential files
    print("\nChecking essential files:")
    success &= check_file_exists("alembic.ini", "alembic.ini exists")
    success &= check_file_exists("migrations/env.py", "migrations/env.py exists")
    success &= check_file_exists("migrations/script.py.mako", "migrations/script.py.mako exists")
    
    # Check for directories
    print("\nChecking directories:")
    success &= check_directory_exists("migrations/versions", "migrations/versions directory exists")
    
    # Check env.py content
    print("\nChecking module configurations:")
    if os.path.isfile("migrations/env.py"):
        success &= check_import("migrations/env.py", 
                               ["run_migrations_offline", "run_migrations_online", "target_metadata"])
    
    # Check database connection
    success &= check_file_exists("app/database/connection.py", "database connection file exists")
    if os.path.isfile("app/database/connection.py"):
        success &= check_import("app/database/connection.py", ["Base", "get_db"])
        
    # Check model imports in env.py
    if os.path.isfile("migrations/env.py"):
        try:
            spec = importlib.util.spec_from_file_location("env", "migrations/env.py")
            env = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(env)
            
            # Check if there are model imports
            model_imports = False
            with open("migrations/env.py", "r") as f:
                content = f.read()
                if "from app.models import" in content:
                    model_imports = True
            
            if model_imports:
                print(f"{Fore.GREEN}✓ Environment correctly imports models{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠ No model imports found in env.py. Autogeneration may not detect all models.{Style.RESET_ALL}")
                success = False
                
        except Exception as e:
            print(f"{Fore.RED}✗ Error checking model imports: {str(e)}{Style.RESET_ALL}")
            success = False
    
    # Final status
    if success:
        print(f"\n{Fore.GREEN}✅ Migration setup verified successfully!{Style.RESET_ALL}")
        return 0
    else:
        print(f"\n{Fore.RED}❌ Migration setup verification failed. Please fix the issues above.{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 