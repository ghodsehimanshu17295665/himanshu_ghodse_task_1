# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Django project files into the container
COPY . /app/

# Install dependencies
RUN pip install -r requirements.txt

RUN chmod +x /app/server-entrypoint.sh

# Expose the port that Django runs on
EXPOSE 8000
