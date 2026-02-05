from datetime import datetime, date
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, computed_field
from configs.llms import ModelConfig
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
THRESHOLD_WORK_COMPLETION = 0.8


class SprintInfo(BaseModel):
    """
    Extracted information about a scrum team member from text.
    """

    sprint_end_date_str: str = Field(
        default=None,
        exclude=True,
        repr=False,
        description="The date of the sprint in YYYY-MM-DD format.",
    )
    user_name: str = Field(
        default=None,
        description="The name of the entity to extract information about usually a scrum team member.",
    )
    project_id: str = Field(
        default=None, description="The project ID associated with the entity."
    )
    sprint_status_type: str = Field(
        default=None,
        description="The status type of the sprint, e.g., 'completed', 'in-progress', etc.",
    )
    sprint_number: int = Field(
        default=None, description="The sprint number associated with the entity."
    )
    assigned_user_stories: int = Field(
        default=None,
        exclude=True,
        description="The number of user_stories assigned to the entity during the sprint.",
    )
    completed_user_stories: int = Field(
        default=None,
        exclude=True,
        description="The number of user_stories completed by the entity during the sprint.",
    )
    pending_user_stories: int = Field(
        default=None,
        exclude=True,
        description="The number of user_stories pending for the entity during the sprint.",
    )

    @staticmethod
    def _convert_str_to_date(date_str: str) -> date | None:
        """Convert a date string in YYYY-MM-DD format to a date object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(
                ValueError(
                    f"Invalid date format: {date_str}. Expected format is YYYY-MM-DD."
                )
            )
            return None

    @computed_field
    @property
    def is_compliant(self) -> bool:
        """Determine if the entity is compliant based on user story completion."""
        if self.assigned_user_stories is None or self.completed_user_stories is None:
            return False
        return (
            self.completed_user_stories
            >= self.assigned_user_stories * THRESHOLD_WORK_COMPLETION
        )

    @computed_field
    @property
    def sprint_end_date(self) -> date | None:
        return self._convert_str_to_date(self.sprint_end_date_str)


info_parser_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at extracting structured information from unstructured text.
    You only extract the following information about a scrum team member from the provided text:
    - user_name
    - project_id
    - sprint_status_type
    - sprint_number
    - sprint_end_date_str (in YYYY-MM-DD format)
    - assigned_user_stories
    - completed_user_stories
    - pending_user_stories
    Provide the extracted information with the specified fields. If any information is missing do not populate them.
    Try to ensure the date is in the YYYY-mm-dd format.Respond in JSON format.NO EXTRA TEXT NOR ANNOTATIONS.
    """,
        ),
        (
            "user",
            """
    Extract the information from the following Text:
    {message}
    """,
        ),
    ]
)


model_config = ModelConfig(local=True, alias="phi-4-mini")
model = ChatOpenAI(
    base_url=model_config.base_url,
    api_key=model_config.api_key,
    model=model_config.model_name,
    temperature=0,
)

SPRINT_INFO_CHAIN = info_parser_prompt | model.with_structured_output(SprintInfo,method="json_mode")
# append a transform to strip the word "json" from the model response
# SPRINT_INFO_CHAIN = (info_parser_prompt | model )
