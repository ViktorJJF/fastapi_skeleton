#!/bin/sh

# Change to project root directory
cd /app

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to apply migrations with retries
apply_migrations() {
    echo "${BLUE}Applying database migrations...${NC}"
    
    # Maximum number of retries
    MAX_RETRIES=5
    RETRY_DELAY=3
    RETRY_COUNT=0
    
    # Try to apply migrations with exponential backoff
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        # Run migrations
        if alembic upgrade head; then
            echo "${GREEN}Migrations applied successfully!${NC}"
            return 0
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                WAIT_TIME=$((RETRY_DELAY * 2 ** (RETRY_COUNT - 1)))
                echo "${YELLOW}Migration failed. Retrying in $WAIT_TIME seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
                sleep $WAIT_TIME
            else
                echo "${RED}Failed to apply migrations after $MAX_RETRIES attempts. Exiting.${NC}"
                return 1
            fi
        fi
    done
    
    return 1
}

# Check if alembic.ini exists
if [ ! -f "alembic.ini" ]; then
    echo "${RED}Error: alembic.ini not found. Migrations will not be applied.${NC}"
    echo "${YELLOW}Starting application without migrations...${NC}"
else
    # Apply migrations with retries
    if ! apply_migrations; then
        echo "${YELLOW}Warning: Continuing without migrations. This may cause application errors.${NC}"
    fi
fi

# Start the application
echo "${BLUE}Starting application...${NC}"