FROM python:3.12-slim-buster  # Use the latest slim Python image

# Set working directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /app

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables (if needed)
# ENV MY_VARIABLE=my_value

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]