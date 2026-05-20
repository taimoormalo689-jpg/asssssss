FROM python:3.9-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Hugging Face Spaces uses port 7860
ENV PORT=7860
EXPOSE 7860

CMD ["python", "grabber_fixed.py"]
