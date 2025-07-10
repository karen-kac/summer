FROM python:3.11-slim

WORKDIR /app

COPY tests/test_requirements.txt .
RUN pip install --no-cache-dir -r test_requirements.txt

COPY . .

CMD ["python", "-m", "pytest"]
