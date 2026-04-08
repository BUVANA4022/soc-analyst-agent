FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port Hugging Face expects
EXPOSE 7860

# This command starts the FastAPI server in the background (port 8000)
# and the Streamlit UI in the foreground (port 7860)
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 7860 --server.address 0.0.0.0