#!/bin/bash
# Database setup script - creates the database and runs migrations

set -e  # Exit on any error

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
RESET=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --reset)
      RESET=true
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      echo "Usage: $0 [--reset]"
      exit 1
      ;;
  esac
  shift
done

echo -e "${BLUE}Setting up database...${NC}"

# Step 1: Create the database if it doesn't exist
echo -e "${YELLOW}Step 1: Creating database...${NC}"
python scripts/create_db.py

# Step 1.5: Reset tables if requested
if $RESET; then
  echo -e "${YELLOW}Step 1.5: Resetting tables...${NC}"
  python scripts/reset_db.py
fi

# Step 2: Run migrations
echo -e "${YELLOW}Step 2: Running migrations...${NC}"
python scripts/db.py migrate

# Step 3: Verify migrations
echo -e "${YELLOW}Step 3: Verifying migrations...${NC}"
python scripts/db.py status

echo -e "${GREEN}Database setup complete!${NC}" 