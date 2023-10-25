# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache -r requirements.txt

# Copy the rest of the project files to the working directory
COPY . .

# Expose the port that your Django application will be running on
EXPOSE 8000

# Set the command to run your Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]