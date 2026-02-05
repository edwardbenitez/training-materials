from typing import TypedDict
from chains.compliance_check import COMPLIANCE_CHECK_CHAIN
from chains.info_extraction import SPRINT_INFO_CHAIN, SprintInfo
from langgraph.graph import END, START, StateGraph
from pydantic import EmailStr
from utils.logging_config import LOGGER

class GraphState(TypedDict):
    sprint_info: str
    sprint_info_extract: SprintInfo | None
    scrum_rules_criteria: str
    sprint_min_stories_criteria: float
    requires_escalation: bool
    escalation_emails: list[EmailStr] | None
    follow_ups: dict[str, bool] | None
    current_follow_up: str | None

def parse_sprint_info_node(state: GraphState) -> GraphState:
    LOGGER.info("Extracting sprint information...")
    sprint_info_extract = SPRINT_INFO_CHAIN.invoke({"message": state["sprint_info"]})

def verify_sprint_is_compliant(state: GraphState) -> GraphState:
    LOGGER.info("Checking if sprint is compliant...")
    sprint_status = COMPLIANCE_CHECK_CHAIN.invoke({"compliant_sprint_criteria": state["scrum_rules_criteria"], "sprint_status_info": state["sprint_info"]})
    if not sprint_status.compliant and state["sprint_info_extract"].assigned_user_stories<state["sprint_min_stories_criteria"]:
        LOGGER.info("Sprint not compliant.")
        state["requires_escalation"] = True

workflow = StateGraph(GraphState)
workflow.add_node("parse_sprint_info", parse_sprint_info_node)
workflow.add_node("is_compliant", verify_sprint_is_compliant)