# MLflow AppInsights Integration

## Overview
This project integrates MLflow with Azure Application Insights to enable comprehensive experiment tracking and monitoring for machine learning workflows.

## Features
- Track ML experiments with MLflow
- Send metrics and logs to Azure Application Insights
- Monitor model performance in real-time
- Centralized logging and telemetry

## Prerequisites
- Python 3.8+
- MLflow
- Azure SDK for Python
- Active Azure subscription

## Installation
```bash
pip install mlflow azure-monitor-opentelemetry
```

## Configuration
Set up your Application Insights connection string:
```python
import os
os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'your-connection-string'
```

## Usage
```python
import mlflow
from mlflow_appinsights import AppInsightsLogger

mlflow.set_tracking_uri("http://localhost:5000")
logger = AppInsightsLogger()

with mlflow.start_run():
    mlflow.log_param("param1", value)
    mlflow.log_metric("accuracy", 0.95)
    logger.log_to_appinsights()
```

## Documentation
See the `/docs` directory for detailed guides.

## License
MIT