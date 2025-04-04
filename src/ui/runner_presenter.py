from typing import List
from src.core.interfaces import IWorkflowRepository, IWebDriver
from src.core.workflow import WorkflowRunner

class RunnerPresenter:
    def __init__(self, view, workflow_repo: IWorkflowRepository, driver: IWebDriver):
        self.view = view
        self.workflow_repo = workflow_repo
        self.driver = driver
        self.workflow_runner = WorkflowRunner(driver, None, workflow_repo)

    def run_workflow(self, workflow_name: str) -> None:
        try:
            self.workflow_runner.run_workflow(workflow_name)
            self.view.show_message(f"Workflow '{workflow_name}' completed successfully.")
        except Exception as e:
            self.view.show_error(f"Error running workflow '{workflow_name}': {str(e)}")

    def list_workflows(self) -> List[str]:
        return self.workflow_repo.list_workflows()
