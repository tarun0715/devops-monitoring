import os 
import time

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(
    title="DevOps Monitoring Platform",
    description="A sample API for an end-to-end DevOps project",
    version="1.0.0",
)

# Count HTTP requests by method, endpoint, and status code.
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

# Measure request processing time in seconds.
HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request processing duration in seconds",
    ["method", "endpoint"],
)


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Record request counts and processing duration."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=str(response.status_code),
    ).inc()

    HTTP_REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response


@app.get("/")
def root():
    return {
        "application": "devops-monitoring-platform",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "devops-monitoring-platform",
    }

@app.get("/bind-mount-test")
def bind_mount_test():
    return{
	"message": "Live Code changes are working!",
	"source": "Mac bind mount",
    }

@app.get("/info")
def application_info():
    return{
	"application": "devops-monitoring-platform",
 	"environment": os.getenv("APP_ENV","development"),
        "managed_by": "docker-compose"
}

# Expose Prometheus metrics at /metrics.
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
