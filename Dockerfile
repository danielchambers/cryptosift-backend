# Use the official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the working directory
COPY . .

# Add the /app directory to PYTHONPATH
ENV PYTHONPATH=/app

# Expose the port on which the Tornado app will run
EXPOSE 8000

# Run the Tornado app when the container starts
CMD ["python", "app/tornado_app/main.py"]