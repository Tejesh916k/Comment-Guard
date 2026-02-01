FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model to cache it in the image (optional but good for speed)
# We can run a small python script to trigger the download or just let it download on first run.
# For simplicity, we let it download on first run.

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
