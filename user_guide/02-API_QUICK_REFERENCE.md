# FastAPI Quick Reference

## Start Server

```bash
# Development (auto-reload)
make api-dev

# Production
make api
```

## Access Points

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Endpoints

### 1. List Available Plots
```bash
GET /api/v1/plots/list?snr=0001&stype=gy&audience=sus
```

### 2. Fetch Raw Data
```bash
POST /api/v1/raw-data
Body: {"snr": "0001", "stype": "gy", "audience": "sus"}
```

### 3. Prepare Data
```bash
POST /api/v1/prepared-data
Body: {"snr": "0001", "stype": "gy", "audience": "sus"}
```

### 4. Generate Plot
```bash
POST /api/v1/plot
Body: {"snr": "0001", "stype": "gy", "audience": "sus", "plot_name": "A12"}
Returns: PDF file
```

### 5. Create Report
```bash
POST /api/v1/report
Body: {"snr": "0001", "stype": "gy", "audience": "sus", "year": "2025"}
Returns: PDF file
```

## cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# List plots
curl "http://localhost:8000/api/v1/plots/list?snr=0001&stype=gy&audience=sus"

# Fetch data
curl -X POST http://localhost:8000/api/v1/raw-data \
  -H "Content-Type: application/json" \
  -d '{"snr": "0001", "stype": "gy", "audience": "sus"}'

# Generate plot
curl -X POST http://localhost:8000/api/v1/plot \
  -H "Content-Type: application/json" \
  -d '{"snr": "0001", "stype": "gy", "audience": "sus", "plot_name": "A12"}' \
  --output plot.pdf

# Create report
curl -X POST http://localhost:8000/api/v1/report \
  -H "Content-Type: application/json" \
  -d '{"snr": "0001", "stype": "gy", "audience": "sus", "year": "2025"}' \
  --output report.pdf
```

## Python Example

```python
import requests

# Start with health check
response = requests.get("http://localhost:8000/health")
print(response.json())

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

## Common Parameters

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `snr` | string | "0001" | School number (zero-padded) |
| `stype` | string | "gy" | School type |
| `audience` | string | "sus" | Target: sus/elt/leh/ubb/aus/all |
| `ubb` | boolean | false | UBB flag |
| `ganztag` | boolean | false | Full-day flag |
| `has_N` | array | ["sus","leh"] | Available audiences |
| `use_cache` | boolean | true | Use cached data |
| `plot_name` | string | "A12" | Specific plot ID |
| `year` | string | "2025" | Report year |

## Testing

```bash
# Run test suite
poetry run python test_api_setup.py

# Run examples
poetry run python example_api_client.py
```

## Documentation

- **Full API Docs**: [API_README.md](API_README.md)
- **Implementation**: [FASTAPI_SUMMARY.md](FASTAPI_SUMMARY.md)
- **Main README**: [README.md](README.md)
