# Use a base Python image
FROM python:3.12.7-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your Python app (from the 'src' directory on the host) into the '/app' directory inside the container
COPY src/ /app/

# Ensure the Python script is executable
RUN chmod +x /app/main.py

# Install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN apt-get update &&\
    apt-get upgrade -y && \
    apt-get install -y zip

RUN pip install chardet

RUN pip install python-docx

# Create a symlink for 'py' to 'python' globally
RUN ln -s /usr/local/bin/python /usr/local/bin/py

# Use ENTRYPOINT to ensure arguments are passed correctly
CMD ["py", "/app/main.py"]