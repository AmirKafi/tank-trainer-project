# Use official Python image
FROM python:3.12

# Install dependencies
RUN apt-get update && apt-get install -y libpq-dev

# Set work directory
WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the FastAPI app files
COPY . .

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
