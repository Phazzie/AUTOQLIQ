import pytest
from unittest.mock import Mock
from src.core.workflow.workflow import Workflow
from src.core.workflow.workflow_runner import WorkflowRunner
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError
from src.core.interfaces import IAction, IWebDriver, IWorkflow
from src.core.action_result import ActionResult
from src.core.exceptions import WorkflowError


class DummyDriver(IWebDriver):
    def get(self, url: str) -> None:
        pass
    def find_element(self, selector: str):
        pass
    def click(self, element) -> None:
        pass
    def type_text(self, element, text: str) -> None:
        pass
    def get_attribute(self, element, attribute: str):
        return None


class DummyWorkflow(IWorkflow):
    def __init__(self, name, actions):
        self._name = name
        self._actions = actions
    @property
    def name(self) -> str:
        return self._name
    @property
    def actions(self) -> list:
        return self._actions
    def add_action(self, action):
        self._actions.append(action)
    def remove_action(self, index: int) -> None:
        self._actions.pop(index)
    def validate(self) -> bool:
        return True
    def to_dict(self) -> dict:
        return {"name": self._name}


class SuccessAction:
    name = "Success"
    def execute(self, driver):
        return ActionResult.success("ok")

class FailAction:
    name = "Fail"
    def execute(self, driver):
        return ActionResult.failure("fail")

class ErrorAction:
    name = "Error"
    def execute(self, driver):
        raise RuntimeError("unexpected")


# Dummy actions for testing
class DummyActionSuccess(IAction):
    action_type = "DummySuccess"
    def __init__(self, name="DummySuccess"):
        self.name = name
    def execute(self, driver, credential_repo=None, context=None):
        return ActionResult.success('ok')
    def validate(self):
        return True
    def to_dict(self):
        return {"type": self.action_type, "name": self.name}
    def get_nested_actions(self):
        return []

class DummyActionFailure(IAction):
    action_type = "DummyFailure"
    def __init__(self, name="DummyFailure"):
        self.name = name
    def execute(self, driver, credential_repo=None, context=None):
        return ActionResult.failure('fail')
    def validate(self):
        return True
    def to_dict(self):
        return {"type": self.action_type, "name": self.name}
    def get_nested_actions(self):
        return []

class DummyActionRaises(IAction):
    action_type = "DummyRaises"
    def __init__(self, name="DummyRaises"):
        self.name = name
    def execute(self, driver, credential_repo=None, context=None):
        raise Exception("Simulated error")
    def validate(self):
        return True
    def to_dict(self):
        return {"type": self.action_type, "name": self.name}
    def get_nested_actions(self):
        return []

@pytest.fixture
def driver_stub():
    return Mock()

def test_run_empty_workflow_returns_empty_list():
    driver = DummyDriver()
    runner = WorkflowRunner(driver)
    wf = DummyWorkflow("EmptyWF", [])
    results = runner.run(wf)
    assert results == []

def test_run_all_success_returns_results():
    driver = DummyDriver()
    runner = WorkflowRunner(driver)
    actions = [SuccessAction(), SuccessAction()]
    wf = DummyWorkflow("AllSuccessWF", actions)
    results = runner.run(wf)
    assert len(results) == 2
    assert all(r.is_success() for r in results)


def test_run_failure_raises_workflow_error():
    driver = DummyDriver()
    runner = WorkflowRunner(driver)
    actions = [SuccessAction(), FailAction(), SuccessAction()]
    wf = DummyWorkflow("FailWF", actions)
    with pytest.raises(WorkflowError) as exc:
        runner.run(wf)
    assert "Fail" in str(exc.value)


def test_run_unexpected_error_raises_wrapped_workflow_error():
    driver = DummyDriver()
    runner = WorkflowRunner(driver)
    actions = [SuccessAction(), ErrorAction()]
    wf = DummyWorkflow("ErrorWF", actions)
    with pytest.raises(WorkflowError) as exc:
        runner.run(wf)
    msg = str(exc.value)
    assert "Unexpected error" in msg or "unexpected" in msg

def test_run_empty_workflow(driver_stub):
    runner = WorkflowRunner(driver_stub)
    wf = Workflow(name='empty', actions=[])
    results = runner.run(wf)
    assert results == []

def test_run_all_success(driver_stub):
    runner = WorkflowRunner(driver_stub)
    wf = Workflow(name='single', actions=[DummyActionSuccess()])
    results = runner.run(wf)
    assert len(results) == 1
    assert results[0].status == ActionStatus.SUCCESS
    assert results[0].message == 'ok'

def test_run_multiple_success(driver_stub):
    runner = WorkflowRunner(driver_stub)
    wf = Workflow(name='multiple', actions=[DummyActionSuccess("Action 1"), DummyActionSuccess("Action 2")])
    results = runner.run(wf)
    assert len(results) == 2
    assert all(r.status == ActionStatus.SUCCESS for r in results)

def test_run_action_failure_stops_workflow(driver_stub):
    runner = WorkflowRunner(driver_stub)
    wf = Workflow(name='failure', actions=[DummyActionSuccess("Action 1"), DummyActionFailure("Action 2"), DummyActionSuccess("Action 3")])
    with pytest.raises(WorkflowError) as excinfo:
        runner.run(wf)
    
    # Check that the error is a WorkflowError and contains information about the failing action
    assert "Action failed during workflow execution" in str(excinfo.value)
    assert "action_name='Action 2'" in str(excinfo.value)
    
    # Check that only the actions before the failure were executed
    # This requires inspecting the runner's internal state or the mock driver's calls
    # For now, we rely on the exception being raised at the correct point.

def test_run_action_raises_exception_wraps_in_workflowerror(driver_stub):
    runner = WorkflowRunner(driver_stub)
    wf = Workflow(name='raises', actions=[DummyActionSuccess("Action 1"), DummyActionRaises("Action 2"), DummyActionSuccess("Action 3")])
    with pytest.raises(WorkflowError) as excinfo:
        runner.run(wf)

    # Check that the error is a WorkflowError and contains information about the failing action
    assert "Unexpected error during workflow execution" in str(excinfo.value)
    assert "action_name='Action 2'" in str(excinfo.value)
    assert "Simulated error" in str(excinfo.value.__cause__)

def test_execute_actions_helper_success(driver_stub):
    runner = WorkflowRunner(driver_stub)
    actions = [DummyActionSuccess("Nested 1"), DummyActionSuccess("Nested 2")]
    results = runner._execute_actions(actions, {}, "Parent Workflow")
    assert len(results) == 2
    assert all(r.status == ActionStatus.SUCCESS for r in results)

def test_execute_actions_helper_failure_raises_actionerror(driver_stub):
    runner = WorkflowRunner(driver_stub)
    actions = [DummyActionSuccess("Nested 1"), DummyActionFailure("Nested 2"), DummyActionSuccess("Nested 3")]
    with pytest.raises(ActionError) as excinfo:
        runner._execute_actions(actions, {}, "Parent Workflow")

    assert "Nested action failed" in str(excinfo.value)
    assert "action_name='Nested 2'" in str(excinfo.value)
