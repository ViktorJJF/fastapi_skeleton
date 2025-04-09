FROM python:3.13-bookworm

# Set working directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app

# Make scripts executable
RUN chmod +x /app/scripts/entrypoint.sh /app/scripts/db.py

# Expose the port the app runs on
EXPOSE 4000

# Set environment variables
ENV PYTHONPATH=/app

# Use the entrypoint script that runs migrations before starting the app
ENTRYPOINT ["/app/scripts/entrypoint.sh"]