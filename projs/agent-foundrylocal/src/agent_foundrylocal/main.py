from chains.info_extraction import SPRINT_INFO_CHAIN
from data.example_sprint import SPRINT
from chains.compliance_check import COMPLIANCE_CHECK_CHAIN
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def main() -> None:
    logger.info("Starting Info Extraction Chain Tests")
    logger.info("====")
    data=SPRINT_INFO_CHAIN.invoke({"message": SPRINT[2]})
    logger.info(data)
    logger.info("====")

    logger.info("Starting Compliance Check Chain Tests")
    logger.info("====")
    rules="""
    - assigned user stories must be greater than zero.
    - pending user stories must be greater than or equal to zero."""
    message = f"""Here is the spint information: 
    - assigned user stories: {data.assigned_user_stories} 
    - completed user stories: {data.completed_user_stories}
    - pending user stories: {data.pending_user_stories}
    """
    compliant = COMPLIANCE_CHECK_CHAIN.invoke({"sprint_status_info": message,"compliant_sprint_criteria":rules})
    logger.info(f"Is the sprint status compliant? {compliant.compliant}")
    logger.info("====")




if __name__ == "__main__":
    main()
