# Use a lightweight Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy all app files
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Healthcheck for container status
HEALTHCHECK CMD curl --fail http://localhost:8501/healthz || exit 1

# Start Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]