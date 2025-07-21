# Marker API

A simple, self-hosted REST API for converting various document formats (PDF, EPUB, MOBI) to clean Markdown using the [marker](https://github.com/datalab-to/marker) library.

The project is built on top of the [fastapi-project-template](https://github.com/ggwozdz90/fastapi-project-template) and follows its architectural principles.

## ✨ Features

- **FastAPI Backend**: A modern, high-performance web framework for building APIs.
- **Marker Integration**: Leverages the powerful `marker` library for high-quality document-to-markdown conversion.
- **Asynchronous Worker Process**: Heavy processing is offloaded to a separate worker process to ensure the API remains responsive.
- **CPU & CUDA Support**: Optimized for both CPU and NVIDIA GPU environments, configurable at runtime.
- **Simple `/markdown` Endpoint**: Straightforward file upload mechanism for document processing.
- **Dockerized**: Ready for deployment with pre-configured `Dockerfile` and `docker-compose` files.
- **Configurable**: Easily configured through environment variables.
- **CI/CD Ready**: Includes GitHub Actions for automated testing, releasing, and Docker image deployment.

## Installation and Setup

### Docker Images

The API is available in two variants:

- **CPU-only** (`ggwozdz/marker-api:cpu-latest`): Smaller image with CPU-only PyTorch
- **GPU-enabled** (`ggwozdz/marker-api:gpu-latest`): Includes CUDA support for GPU acceleration
- **Default** (`ggwozdz/marker-api:latest`): Points to the GPU-enabled version

### Docker (recommended)

```bash
# CPU version
docker run -d -p 8000:8000 \
  -e DEVICE=cpu \
  ggwozdz/marker-api:cpu-latest

# GPU version  
docker run -d -p 8000:8000 \
  -e DEVICE=cuda \
  --gpus all \
  ggwozdz/marker-api:gpu-latest

# Alternative: use unversioned tags (GPU version)
docker run -d -p 8000:8000 \
  -e DEVICE=cuda \
  --gpus all \
  ggwozdz/marker-api:latest
```

### Poetry (development)

```bash
git clone <repository>
cd embed-api
poetry install
poetry run python src/main.py
```

## API Endpoints

Full API documentation available at: `http://localhost:8000/docs`

### 1. Health Check

```http
GET /healthcheck
```

Checks the application status.

### 2. Generate Markdown

```http
POST /markdown
Content-Type: multipart/form-data

file=@/path/to/your/document.pdf
```

Generates Markdown from the uploaded document file.

## Configuration

The application is configured via environment variables:

| Variable | Description | Default value |
|----------|-------------|---------------|
| `DEVICE` | Device: `cpu` or `cuda` | `cpu` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `FASTAPI_HOST` | Server host | `127.0.0.1` |
| `FASTAPI_PORT` | Server port | `8000` |

## License

MIT License
