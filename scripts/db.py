#!/usr/bin/env python3
"""
Database migration utility script.
Similar to Rails migration commands.
"""

import os
import sys
import argparse
import subprocess
import importlib.util
from pathlib import Path


def create_migration(args):
    """Create a new migration."""
    message = args.message
    if not message:
        print("Error: Migration message is required")
        sys.exit(1)

    cmd = ["alembic", "revision", "--autogenerate", "-m", message]
    print(f"Creating migration: {message}...")
    subprocess.run(cmd)


def create_empty_migration(args):
    """Create an empty migration for manual operations."""
    message = args.message
    if not message:
        print("Error: Migration message is required")
        sys.exit(1)

    cmd = ["alembic", "revision", "-m", message]
    print(f"Creating empty migration: {message}...")
    subprocess.run(cmd)


def create_branch_migration(args):
    """Create a branch migration from a specified parent."""
    message = args.message
    parent = args.parent
    if not message:
        print("Error: Migration message is required")
        sys.exit(1)
    if not parent:
        print("Error: Parent revision is required")
        sys.exit(1)

    cmd = ["alembic", "revision", "-m", message, "--head", parent]
    print(f"Creating branch migration: {message} from parent {parent}...")
    subprocess.run(cmd)


def migrate(args):
    """Run all pending migrations or upgrade to a specific revision."""
    revision = args.revision if args.revision else "head"
    cmd = ["alembic", "upgrade", revision]
    print(f"Migrating database to: {revision}...")
    subprocess.run(cmd)


def rollback(args):
    """Rollback migrations."""
    step = args.step if args.step else 1
    cmd = ["alembic", "downgrade", f"-{step}"]
    print(f"Rolling back {step} migration(s)...")
    subprocess.run(cmd)


def reset(args):
    """Reset the database (down to base and up to head)."""
    print("Resetting database...")
    subprocess.run(["alembic", "downgrade", "base"])
    subprocess.run(["alembic", "upgrade", "head"])


def status(args):
    """Show current migration status."""
    print("Current migration status:")
    subprocess.run(["alembic", "current"])


def history(args):
    """Show migration history."""
    print("Migration history:")
    verbose = ["-v"] if args.verbose else []
    range_option = []
    if args.range:
        range_option = ["-r", args.range]
    subprocess.run(["alembic", "history"] + verbose + range_option)


def stamp(args):
    """Stamp the revision, without running migrations."""
    if not args.revision:
        print("Error: Revision is required for stamp command")
        sys.exit(1)

    cmd = ["alembic", "stamp", args.revision]
    print(f"Stamping database as: {args.revision}...")
    subprocess.run(cmd)


def show(args):
    """Show details of a revision."""
    if not args.revision:
        print("Error: Revision is required for show command")
        sys.exit(1)

    cmd = ["alembic", "show", args.revision]
    print(f"Showing details for revision: {args.revision}...")
    subprocess.run(cmd)


def generate_sql(args):
    """Generate SQL for migrations without executing them."""
    if not args.revision:
        args.revision = "head"

    output_file = args.output if args.output else "migration.sql"
    cmd = ["alembic", "upgrade", args.revision, "--sql"]

    print(f"Generating SQL for migration to {args.revision} in {output_file}...")
    with open(output_file, "w") as f:
        subprocess.run(cmd, stdout=f)

    print(f"SQL script generated: {output_file}")


def heads(args):
    """Show current branch heads."""
    print("Current branch heads:")
    verbose = ["-v"] if args.verbose else []
    subprocess.run(["alembic", "heads"] + verbose)


def branches(args):
    """Show current branch points."""
    print("Current branch points:")
    verbose = ["-v"] if args.verbose else []
    subprocess.run(["alembic", "branches"] + verbose)


def ensure_alembic_installed():
    """Check if alembic is installed and importable."""
    try:
        import alembic

        return True
    except ImportError:
        print(
            "Error: Alembic is not installed. Please install it with 'pip install alembic'."
        )
        sys.exit(1)


def verify_alembic_files():
    """Verify that all required alembic files exist."""
    project_root = Path(".").resolve()
    required_files = [
        project_root / "alembic.ini",
        project_root / "migrations" / "env.py",
        project_root / "migrations" / "script.py.mako",
    ]
    required_dirs = [
        project_root / "migrations" / "versions",
    ]

    for file_path in required_files:
        if not file_path.is_file():
            print(f"Error: Required file {file_path} not found.")
            return False

    for dir_path in required_dirs:
        if not dir_path.is_dir():
            print(f"Error: Required directory {dir_path} not found.")
            return False

    return True


def main():
    """Main entry point for the script."""
    # Ensure alembic is installed
    ensure_alembic_installed()

    parser = argparse.ArgumentParser(description="Database migration utility")
    subparsers = parser.add_subparsers(help="Commands", dest="command")

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", nargs="?", help="Migration message")
    create_parser.set_defaults(func=create_migration)

    # Create empty migration command
    empty_parser = subparsers.add_parser(
        "create-empty", help="Create an empty migration for manual operations"
    )
    empty_parser.add_argument("message", nargs="?", help="Migration message")
    empty_parser.set_defaults(func=create_empty_migration)

    # Create branch migration command
    branch_parser = subparsers.add_parser(
        "create-branch", help="Create a branch migration from a specific parent"
    )
    branch_parser.add_argument("message", nargs="?", help="Migration message")
    branch_parser.add_argument("--parent", "-p", help="Parent revision")
    branch_parser.set_defaults(func=create_branch_migration)

    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run pending migrations")
    migrate_parser.add_argument(
        "revision", nargs="?", help="Target revision (default: head)"
    )
    migrate_parser.set_defaults(func=migrate)

    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument(
        "step",
        nargs="?",
        type=int,
        help="Number of migrations to rollback (default: 1)",
    )
    rollback_parser.set_defaults(func=rollback)

    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset the database")
    reset_parser.set_defaults(func=reset)

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Show current migration status"
    )
    status_parser.set_defaults(func=status)

    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose history"
    )
    history_parser.add_argument(
        "-r", "--range", help="Range of revisions (e.g., 'base:head', '-3:current')"
    )
    history_parser.set_defaults(func=history)

    # Stamp command
    stamp_parser = subparsers.add_parser(
        "stamp", help="Stamp the database with the given revision"
    )
    stamp_parser.add_argument("revision", help="Revision to stamp")
    stamp_parser.set_defaults(func=stamp)

    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a revision")
    show_parser.add_argument("revision", help="Revision to show")
    show_parser.set_defaults(func=show)

    # Generate SQL command
    sql_parser = subparsers.add_parser(
        "sql", help="Generate SQL script for migrations without executing"
    )
    sql_parser.add_argument(
        "revision", nargs="?", help="Target revision (default: head)"
    )
    sql_parser.add_argument(
        "--output", "-o", help="Output file (default: migration.sql)"
    )
    sql_parser.set_defaults(func=generate_sql)

    # Heads command
    heads_parser = subparsers.add_parser("heads", help="Show current branch heads")
    heads_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )
    heads_parser.set_defaults(func=heads)

    # Branches command
    branches_parser = subparsers.add_parser(
        "branches", help="Show current branch points"
    )
    branches_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )
    branches_parser.set_defaults(func=branches)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    # Set the working directory to project root
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Verify alembic files
    if not verify_alembic_files():
        print("Error: Alembic environment not properly set up.")
        sys.exit(1)

    # Call the appropriate function
    args.func(args)


if __name__ == "__main__":
    main()
