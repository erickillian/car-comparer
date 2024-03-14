# Use an official Python runtime as a parent image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the wait-for-db script
COPY wait-for-db.sh /usr/wait-for-db.sh

# Make the script executable
RUN chmod +x /usr/wait-for-db.sh

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

CMD ["/usr/wait-for-db.sh", "db", "mydatabase", "python", "manage.py", "runserver", "0.0.0.0:80"]
