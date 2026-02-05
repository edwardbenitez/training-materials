from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from configs.llms import ModelConfig


class ComplianceCheck(BaseModel):
    compliant: bool = Field(
        description="Indicates whether the user sprint status is compliant with the defined standards. True if compliant, False otherwise."
    )

def validate_output(state):
  # Post-process structured response
  response = state["structured_response"]
  # ... validation logic
  return {"structured_response": validated_response}

compliance_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Determine if the following sprint status information is compliant or not based on the following criteria.
            
            Compliance Criteria:
            {compliant_sprint_criteria}.
            
            Respond with a JSON object containing a single boolean field 'compliant' set to true if the sprint status information meets the compliance criteria, or false otherwise.
            NO EXTRA TEXT NOR ANNOTATIONS.
        """,
        ),(
            "user",
            """Indicate if the following sprint status information is compliant:
            {sprint_status_info}
            """
        )
    ]
)
model_config = ModelConfig(local=True, alias="phi-4-mini")
compliance_llm = ChatOpenAI(
    base_url=model_config.base_url,
    api_key=model_config.api_key,
    model=model_config.model_name,
    temperature=model_config.temperature,
)

COMPLIANCE_CHECK_CHAIN = compliance_prompt | compliance_llm.with_structured_output(
    ComplianceCheck,method="json_mode"
)
