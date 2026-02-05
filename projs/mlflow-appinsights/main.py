import mlflow
from typing import List, Dict, Optional
import logging
from azure.monitor.opentelemetry import configure_azure_monitor
from mlflow.models import infer_signature
from opentelemetry import metrics
import os
from opentelemetry._logs import get_logger_provider
import requests

class CustomModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        super().__init__()
        self.logger_name = "pyfunclog"

    def load_context(self, context):
        appinsights_conn = os.environ["APPINSIGHTS_CONN_STRING"]

        configure_azure_monitor(
            connection_string=appinsights_conn, logger_name=self.logger_name
        )
        self._meter = metrics.get_meter_provider().get_meter(
            "otel_azure_monitor_counter"
        )

    def predict(self, model_input: List[dict[str, str]]) -> List[str]:
        _logger = logging.getLogger(self.logger_name)
        try:
            _logger.setLevel(logging.INFO)
            counter = self._meter.create_counter("counter")
            counter.add(1.0, {"ammount_msg": f"{len(model_input)}"})
            counter.add(5.0, {"test_key2": "test_value"})
            counter.add(3.0, {"test_key": "test_value2"})

            _logger.error(f"Predicting on {len(model_input)} messages - from inference")
            result = [msg.get("content") for msg in model_input]
            _logger.error("Prediction completed successfully - from inference")
            provider = get_logger_provider()
            if hasattr(provider, "force_flush"):
                provider.force_flush()
                _logger.error("force_flush completed")
            return result
        except:
            _logger.error("Prediction failed - from inference")
            return ["Hello", "Hi"]
        finally:
            url = "https://api.restful-api.dev/objects?id=3&id=5&id=10"
            response = requests.get(url)
            data = response.json()
            _logger.error(data)

            provider = get_logger_provider()
            if hasattr(provider, "force_flush"):
                provider.force_flush()
                _logger.error("force_flush completed")


# Construct the model and test
model = CustomModel()

# The input_example can be a list of Message objects as defined in the type hint
input_example = [
    {"role": "system", "content": "Hello"},
    {"role": "user", "content": "Hi"},
]
assert model.predict(input_example) == ["Hello", "Hi"]

assert model.predict(input_example) == ["Hello", "Hi"]
signature = infer_signature(input_example, model.predict(input_example))
# Log the model
with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        python_model=model,
        name="model",
        registered_model_name="main.mlops.custom_model_v2",
        input_example=input_example,
        extra_pip_requirements=[
            "azure-core==1.38.0",
            "azure-monitor-opentelemetry==1.4.1",
        ],
        # signature=signature
    )
