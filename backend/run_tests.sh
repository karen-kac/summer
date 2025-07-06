echo "🐳 Building Docker image for pytest..."
docker build -f tests/Dockerfile -t my-pytest .

echo "✅ Running tests inside Docker..."
docker run --rm my-pytest
