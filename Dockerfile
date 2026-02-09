# Use a slim version of Python
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install pipenv
RUN pip install pipenv

# Copy dependency files first 
COPY Pipfile Pipfile.lock ./

# Install dependencies directly into the container's system
RUN pipenv install --system --deploy

# Copy the rest of code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]