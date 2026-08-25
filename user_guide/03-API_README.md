# PyReporter API

FastAPI service layer for the pyreporter survey report generation pipeline.


### Starting the API Server

```bash
# Development server with auto-reload
poetry run uvicorn pyreporter.api:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
poetry run python -m pyreporter.api
```

The API will be available at:
- **API Base**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### 1. Get Raw Data
**POST** `/api/v1/raw-data`

Fetch raw survey data from LimeSurvey with caching support.

**Request Body:**
```json
{
  "snr": "0001",
  "stype": "gy",
  "audience": "sus",
  "ubb": false,
  "ganztag": false,
  "has_N": ["sus", "leh"],
  "use_cache": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Fetched raw data for school 0001",
  "rows": 150,
  "syear": "2025",
  "result_n": "150",
  "columns": ["sid", "surveyls_title", "id", "vars", "vals"],
  "data_preview": [...]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/raw-data \
  -H "Content-Type: application/json" \
  -d '{
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "ubb": false,
    "ganztag": false,
    "has_N": ["sus", "leh"]
  }'
```

### 2. Get Prepared Data
**POST** `/api/v1/prepared-data`

Transform raw data into plot-ready format with metadata.

**Request Body:**
```json
{
  "snr": "0001",
  "stype": "gy",
  "audience": "sus",
  "ubb": false,
  "ganztag": false,
  "has_N": ["sus", "leh"],
  "use_cache": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Prepared data for school 0001",
  "plots_count": 25,
  "sname": "Example School",
  "syear": "2025",
  "report_name": "gy_report",
  "plots_available": ["A12", "A3a", "B01", ...]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/prepared-data \
  -H "Content-Type: application/json" \
  -d '{
    "snr": "0001",
    "stype": "gy",
    "audience": "sus"
  }'
```

### 3. Generate a Single Plot
**POST** `/api/v1/plot`

Generate a specific plot and return as PDF.

**Request Body:**
```json
{
  "snr": "0001",
  "stype": "gy",
  "audience": "sus",
  "plot_name": "A12",
  "ubb": false,
  "ganztag": false,
  "has_N": ["sus", "leh"],
  "use_cache": true
}
```

**Response:**
Returns PDF file download.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/plot \
  -H "Content-Type: application/json" \
  -d '{
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "plot_name": "A12"
  }' \
  --output plot_A12.pdf
```

### 4. Create Complete Report
**POST** `/api/v1/report`

Generate complete PDF report with all plots.

**Request Body:**
```json
{
  "snr": "0001",
  "stype": "gy",
  "audience": "sus",
  "ubb": false,
  "ganztag": false,
  "has_N": ["sus", "leh"],
  "year": "2025",
  "duration": "2",
  "use_cache": true
}
```

**Response:**
Returns complete PDF report.

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/report \
  -H "Content-Type: application/json" \
  -d '{
    "snr": "0001",
    "stype": "gy",
    "audience": "sus",
    "year": "2025"
  }' \
  --output report.pdf
```

### 5. List Available Plots
**GET** `/api/v1/plots/list`

List all available plots for a configuration (lightweight, no data fetching).

**Query Parameters:**
- `snr`: School number (required)
- `stype`: School type (required)
- `audience`: Target audience (required)
- `ubb`: UBB flag (default: false)
- `ganztag`: Full-day school flag (default: false)

**Example:**
```bash
curl "http://localhost:8000/api/v1/plots/list?snr=0001&stype=gy&audience=sus"
```

**Response:**
```json
{
  "status": "success",
  "snr": "0001",
  "report": "gy_report",
  "audience": "sus",
  "plots": ["A12", "A3a", "B01", ...],
  "count": 25
}
```

### 6. Health Check
**GET** `/health`

Simple health check endpoint.

**Example:**
```bash
curl http://localhost:8000/health
```

## Request Parameters

### Common Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `snr` | string | Yes | - | School number (zero-padded) |
| `stype` | string | Yes | - | School type (e.g., "gy") |
| `audience` | string | Yes | - | Target audience: sus, elt, leh, ubb, aus, all |
| `ubb` | boolean | No | false | UBB flag |
| `ganztag` | boolean | No | false | Full-day school flag |
| `has_N` | array[string] | No | ["sus", "leh"] | Available audiences |
| `use_cache` | boolean | No | true | Use cached data |

### Plot-Specific Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plot_name` | string | Yes | Plot ID (e.g., "A12", "A3a") |

### Report-Specific Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `year` | string | No | "2025" | Report year |
| `duration` | string | No | "2" | Survey duration |

## Audience Codes

- `sus` - Students (Schülerinnen und Schüler)
- `elt` - Parents (Eltern)
- `leh` - Teachers (Lehrkräfte)
- `ubb` - Classroom observations (Unterrichtsbeobachtungen)
- `aus` - Trainers (Ausbilder)
- `all` - All groups

## School Types

- `gy` - Gymnasium
- (Other types as defined in your metadata)

## Error Handling

All endpoints return standard HTTP status codes:

- **200** - Success
- **404** - Resource not found (e.g., plot doesn't exist)
- **500** - Internal server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Caching

The API uses the same caching system as the CLI pipeline:

- **Raw data cache**: `.cache/raw_*.pkl` (cached by `snr`, `ubb`)
- **Prepared data cache**: `.cache/prepared_*.pkl` (cached by all params)

To bypass cache:
```bash
# Set use_cache to false in request
{
  "snr": "0001",
  "use_cache": false
}

# Or clear cache manually
make clean-cache
```

## Production Deployment

### Using Gunicorn

```bash
poetry run gunicorn pyreporter.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.14-slim

WORKDIR /app
COPY . /app

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Ensure Quarto is installed
RUN apt-get update && apt-get install -y quarto

EXPOSE 8000
CMD ["uvicorn", "pyreporter.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Required (same as CLI):
```bash
LIME_API_URL=https://your-limesurvey.com/admin/remotecontrol
LIME_USERNAME=your_username
LIME_PASSWORD=your_password
```

Optional:
```bash
NO_CACHE=true  # Disable caching globally
```

## Testing the API

### Using the Interactive Docs

1. Start the server: `poetry run uvicorn pyreporter.api:app --reload`
2. Open http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in parameters and click "Execute"

### Using Python Requests

```python
import requests

# Fetch raw data
response = requests.post(
    "http://localhost:8000/api/v1/raw-data",
    json={
        "snr": "0001",
        "stype": "gy",
        "audience": "sus"
    }
)
data = response.json()
print(f"Fetched {data['rows']} rows")

# Generate report
response = requests.post(
    "http://localhost:8000/api/v1/report",
    json={
        "snr": "0001",
        "stype": "gy",
        "audience": "sus",
        "year": "2025"
    }
)

# Save PDF
with open("report.pdf", "wb") as f:
    f.write(response.content)
```

## Architecture

The API is a thin wrapper around the existing pyreporter pipeline:

```
API Request → FastAPI → pyreporter modules → Response
                ↓
        ┌─────────────────┐
        │  fetch.py       │  Fetches raw data
        ├─────────────────┤
        │  prepare.py     │  Prepares plot data
        ├─────────────────┤
        │  plot.py        │  Generates plots
        ├─────────────────┤
        │  render_pdf.py  │  Renders PDF
        └─────────────────┘
```

Each endpoint reuses the existing pipeline functions with proper error handling and response formatting.
