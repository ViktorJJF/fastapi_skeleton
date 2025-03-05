FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./app /app

# Expose the port the app runs on
EXPOSE 4000

# Set environment variables (if needed)
# ENV MY_VARIABLE=my_value

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]