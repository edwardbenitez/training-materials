import mlflow
from typing import List, Dict, Optional
import pydantic
import logging
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace, metrics
from opencensus.ext.azure.log_exporter import AzureLogHandler

appinsights_conn="InstrumentationKey=994bda67-184e-44cf-b956-9415b4f04703;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/;LiveEndpoint=https://westus2.livediagnostics.monitor.azure.com/;ApplicationId=d0b0e7da-3028-4774-8c2f-f04c64403943"

# Configure Azure Monitor with the connection string
configure_azure_monitor(connection_string=appinsights_conn)

# Get tracer and logger for Application Insights
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
azure_handler = AzureLogHandler(connection_string=appinsights_conn)
logger.addHandler(azure_handler)

class Message(pydantic.BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, str]] = None


class CustomModel(mlflow.pyfunc.PythonModel):
    def predict(self, model_input: List[Message]) -> List[str]:
        # Signature automatically inferred from type hints!
        with tracer.start_as_current_span("predict") as span:
            logger.info(f"Predicting on {len(model_input)} messages")
            span.set_attribute("input_count", len(model_input))
            try:
                result = [msg.content for msg in model_input]
                logger.info("Prediction completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error during prediction: {str(e)}")
                span.set_attribute("error", True)
                raise


# Log model - signature is auto-generated from type hints
with mlflow.start_run():
    mlflow.pyfunc.log_model(
        artifact_path="model",
        registered_model_name="main.mlops.custom_model",
        python_model=CustomModel(),
        input_example=[
            {"role": "user", "content": "Hello"}
        ],  # Validates against type hints
    )