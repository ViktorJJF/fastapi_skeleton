.PHONY: help start stop db-create db-create-empty db-create-branch db-migrate db-rollback db-reset db-status db-history db-stamp db-show db-sql db-heads db-branches db-verify db-create-database db-setup db-reset-tables db-setup-reset

help:
	@echo "Available commands:"
	@echo "  make start           - Start the application"
	@echo "  make stop            - Stop the application"
	@echo ""
	@echo "Database Migration Commands:"
	@echo "  make db-setup        - Setup the database and run migrations"
	@echo "  make db-setup-reset  - Reset tables, then setup database and run migrations"
	@echo "  make db-create-database [NAME=\"db_name\"] - Create a new database"
	@echo "  make db-create NAME=\"migration name\"  - Create a new database migration"
	@echo "  make db-create-empty NAME=\"migration name\" - Create an empty migration for manual operations"
	@echo "  make db-create-branch NAME=\"migration name\" PARENT=\"parent_revision\" - Create a branch migration"
	@echo "  make db-migrate [REVISION=\"revision\"] - Run database migrations (default: head)"
	@echo "  make db-rollback [STEP=n]  - Rollback n migrations (default: 1)"
	@echo "  make db-reset        - Reset the database (rollback all and migrate)"
	@echo "  make db-reset-tables - Drop all tables and reset migration state"
	@echo "  make db-status       - Show current migration status"
	@echo "  make db-history [RANGE=\"x:y\"] - Show migration history with optional range"
	@echo "  make db-stamp REVISION=\"revision\" - Stamp the database with revision without running migrations"
	@echo "  make db-show REVISION=\"revision\" - Show details of a specific revision"
	@echo "  make db-sql [REVISION=\"revision\"] [OUTPUT=\"file.sql\"] - Generate SQL script for migrations"
	@echo "  make db-heads        - Show current branch heads"
	@echo "  make db-branches     - Show current branch points"
	@echo "  make db-verify       - Verify the migration setup"

start:
	docker-compose up -d

stop:
	docker-compose down

db-setup:
	docker-compose exec albedo scripts/setup_db.sh

db-setup-reset:
	docker-compose exec albedo scripts/setup_db.sh --reset

db-reset-tables:
	docker-compose exec albedo python scripts/reset_db.py

db-create-database:
	@if [ -z "$(NAME)" ]; then \
		docker-compose exec albedo python scripts/create_db.py; \
	else \
		docker-compose exec albedo python scripts/create_db.py --name "$(NAME)"; \
	fi

db-create:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME is required. Usage: make db-create NAME=\"migration name\""; \
		exit 1; \
	fi
	docker-compose exec albedo python scripts/db.py create "$(NAME)"

db-create-empty:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME is required. Usage: make db-create-empty NAME=\"migration name\""; \
		exit 1; \
	fi
	docker-compose exec albedo python scripts/db.py create-empty "$(NAME)"

db-create-branch:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME is required."; \
		exit 1; \
	fi
	@if [ -z "$(PARENT)" ]; then \
		echo "Error: PARENT is required."; \
		exit 1; \
	fi
	docker-compose exec albedo python scripts/db.py create-branch "$(NAME)" --parent "$(PARENT)"

db-migrate:
	@if [ -z "$(REVISION)" ]; then \
		docker-compose exec albedo python scripts/db.py migrate; \
	else \
		docker-compose exec albedo python scripts/db.py migrate "$(REVISION)"; \
	fi

db-rollback:
	@if [ -z "$(STEP)" ]; then \
		docker-compose exec albedo python scripts/db.py rollback; \
	else \
		docker-compose exec albedo python scripts/db.py rollback $(STEP); \
	fi

db-reset:
	docker-compose exec albedo python scripts/db.py reset

db-status:
	docker-compose exec albedo python scripts/db.py status

db-history:
	@if [ -z "$(RANGE)" ]; then \
		docker-compose exec albedo python scripts/db.py history -v; \
	else \
		docker-compose exec albedo python scripts/db.py history -v --range "$(RANGE)"; \
	fi

db-stamp:
	@if [ -z "$(REVISION)" ]; then \
		echo "Error: REVISION is required. Usage: make db-stamp REVISION=\"revision\""; \
		exit 1; \
	fi
	docker-compose exec albedo python scripts/db.py stamp "$(REVISION)"

db-show:
	@if [ -z "$(REVISION)" ]; then \
		echo "Error: REVISION is required. Usage: make db-show REVISION=\"revision\""; \
		exit 1; \
	fi
	docker-compose exec albedo python scripts/db.py show "$(REVISION)"

db-sql:
	@if [ -z "$(REVISION)" ] && [ -z "$(OUTPUT)" ]; then \
		docker-compose exec albedo python scripts/db.py sql; \
	elif [ -z "$(OUTPUT)" ]; then \
		docker-compose exec albedo python scripts/db.py sql "$(REVISION)"; \
	elif [ -z "$(REVISION)" ]; then \
		docker-compose exec albedo python scripts/db.py sql --output "$(OUTPUT)"; \
	else \
		docker-compose exec albedo python scripts/db.py sql "$(REVISION)" --output "$(OUTPUT)"; \
	fi

db-heads:
	docker-compose exec albedo python scripts/db.py heads -v

db-branches:
	docker-compose exec albedo python scripts/db.py branches -v

db-verify:
	python scripts/verify_migrations.py 