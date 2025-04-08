#!/usr/bin/env python
"""
AutoQliq Context Files Exporter

This script exports the essential context files for the AutoQliq project,
organized into groups based on their importance for providing context in a new chat window.

The files are exported to a 'context_export' folder with clear markers for each group.
"""

import os
import shutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('context_export.log')
    ]
)
logger = logging.getLogger(__name__)

# Define the groups of files
GROUP_1_MUST_ADD = [
    "src/core/interfaces/action.py",
    "src/core/interfaces/repository.py",
    "src/core/interfaces/webdriver.py",
    "src/core/interfaces/service.py",
    "src/core/actions/base.py",
    "src/core/actions/factory.py",
    "src/core/workflow/runner.py",
    "src/core/exceptions.py",
    "src/core/action_result.py",
    "src/ui/interfaces/presenter.py",
    "src/ui/interfaces/view.py",
    "src/ui/presenters/base_presenter.py",
    "src/ui/views/base_view.py",
    "src/config.py",
    "config.ini",
    "src/main_ui.py",
    "README.md"
]

GROUP_2_SHOULD_ADD = [
    "src/application/services/credential_service.py",
    "src/application/services/workflow_service.py",
    "src/application/services/webdriver_service.py",
    "src/application/services/reporting_service.py",
    "src/core/actions/conditional_action.py",
    "src/core/actions/loop_action.py",
    "src/core/actions/error_handling_action.py",
    "src/infrastructure/common/error_handling.py",
    "src/infrastructure/common/logging_utils.py",
    "src/ui/common/ui_factory.py",
    "src/ui/dialogs/action_editor_dialog.py",
    "src/ui/dialogs/credential_manager_dialog.py",
    "src/ui/views/settings_view.py",
    "src/ui/presenters/settings_presenter.py"
]

GROUP_3_COULD_ADD = [
    # Repository implementations
    "src/infrastructure/repositories/file_system_workflow_repository.py",
    "src/infrastructure/repositories/database_workflow_repository.py",
    # WebDriver implementation
    "src/infrastructure/webdrivers/selenium_driver.py",
    # Standard actions
    "src/core/actions/navigation.py",
    "src/core/actions/interaction.py",
    # Unit tests
    "tests/unit/core/test_workflow.py",
    "tests/unit/application/test_credential_service.py"
]

def create_export_folder():
    """Create the export folder with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_folder = f"context_export_{timestamp}"

    if not os.path.exists(export_folder):
        os.makedirs(export_folder)
        logger.info(f"Created export folder: {export_folder}")

    return export_folder

def export_file(file_path, export_folder, group_marker):
    """Export a single file to the export folder with group marker."""
    # Normalize path
    normalized_path = os.path.normpath(file_path)

    # Check if file exists
    if not os.path.exists(normalized_path):
        logger.warning(f"File not found: {normalized_path}")
        return False

    # Read file content
    try:
        with open(normalized_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file {normalized_path}: {e}")
        return False

    # Create the export content with markers
    export_content = f"""
########## START FILE: {file_path} ##########
# GROUP: {group_marker}

{content}

########## END FILE: {file_path} ##########

"""

    # Write to the export file
    export_file_path = os.path.join(export_folder, "context_files.txt")
    try:
        with open(export_file_path, 'a', encoding='utf-8') as f:
            f.write(export_content)
        logger.info(f"Exported file: {normalized_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to export file: {e}")
        return False

def create_group_summary(export_folder, group_files, group_name, group_description):
    """Create a summary for a group of files."""
    summary_content = f"""
==================================================
{group_name}
==================================================
{group_description}

Files in this group:
"""

    for file_path in group_files:
        normalized_path = os.path.normpath(file_path)
        exists = "✓" if os.path.exists(normalized_path) else "✗"
        summary_content += f"  {exists} {file_path}\n"

    summary_content += "\n\n"

    # Write to the summary file
    summary_file_path = os.path.join(export_folder, "context_summary.txt")
    try:
        with open(summary_file_path, 'a', encoding='utf-8') as f:
            f.write(summary_content)
        logger.info(f"Added summary for {group_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to write to summary file: {e}")
        return False

def create_prompt_template(export_folder):
    """Create a template for the first prompt in a new chat window."""
    template_content = """
# First Prompt Template for New Chat Window

```
Okay, let's resume work on the AutoQliq project.

**Goal for this Session:**
[DESCRIBE YOUR IMMEDIATE GOAL HERE]

**Essential Context Files:**

[PASTE SELECTED FILES FROM context_files.txt HERE]

**What I'd like to accomplish:**
[DESCRIBE SPECIFIC TASKS OR FEATURES YOU WANT TO IMPLEMENT]

Please analyze these files and help me [SPECIFIC REQUEST].
```

Instructions:
1. Copy this template
2. Fill in the sections in [BRACKETS]
3. For the Essential Context Files section, copy and paste the relevant files from context_files.txt
   - Always include all Group 1 (MUST ADD) files
   - Include Group 2 (SHOULD ADD) files relevant to your current task
   - Include Group 3 (COULD ADD) files only if directly modifying them
4. Remove these instructions before sending the prompt
"""

    # Write to the template file
    template_file_path = os.path.join(export_folder, "first_prompt_template.txt")
    try:
        with open(template_file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        logger.info(f"Created prompt template")
        return True
    except Exception as e:
        logger.error(f"Failed to write prompt template: {e}")
        return False

def main():
    """Main function to run the script."""
    # Create export folder
    export_folder = create_export_folder()

    # Create empty files to start fresh
    open(os.path.join(export_folder, "context_files.txt"), 'w').close()
    open(os.path.join(export_folder, "context_summary.txt"), 'w').close()

    # Add header to summary file
    with open(os.path.join(export_folder, "context_summary.txt"), 'w', encoding='utf-8') as f:
        f.write(f"""
# AutoQliq Context Files Summary
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This file provides a summary of the context files exported for the AutoQliq project.
The files are organized into three groups based on their importance for providing context in a new chat window.

""")

    # Export Group 1 files
    create_group_summary(
        export_folder,
        GROUP_1_MUST_ADD,
        "Group 1: MUST ADD (Essential Contracts, Foundations, Wiring)",
        "These files define the core structure, interfaces, and how components are expected to interact. "
        "Without these, the AI cannot generate compatible or correctly integrated code."
    )

    for file_path in GROUP_1_MUST_ADD:
        export_file(file_path, export_folder, "Group 1: MUST ADD")

    # Export Group 2 files
    create_group_summary(
        export_folder,
        GROUP_2_SHOULD_ADD,
        "Group 2: SHOULD PROBABLY ADD (Key Implementations & Recent Complex Logic)",
        "These provide context on established patterns, recent complex additions, and key service implementations "
        "that presenters interact with. They significantly help in understanding how things currently work."
    )

    for file_path in GROUP_2_SHOULD_ADD:
        export_file(file_path, export_folder, "Group 2: SHOULD PROBABLY ADD")

    # Export Group 3 files
    create_group_summary(
        export_folder,
        GROUP_3_COULD_ADD,
        "Group 3: COULD ADD (Specific Examples - If Relevant to Next Task)",
        "These are less critical for general context but might be useful if the very next task involves "
        "modifying or testing them specifically. Add only if needed."
    )

    for file_path in GROUP_3_COULD_ADD:
        export_file(file_path, export_folder, "Group 3: COULD ADD")

    # Create prompt template
    create_prompt_template(export_folder)

    # Print summary
    print(f"\nContext files exported to {export_folder}/")
    print(f"  - context_files.txt: Contains all exported files with markers")
    print(f"  - context_summary.txt: Contains a summary of all files by group")
    print(f"  - first_prompt_template.txt: Template for the first prompt in a new chat window")

    logger.info("Export completed successfully")

if __name__ == "__main__":
    main()




########## START FILE: src/core/interfaces/action.py ##########
"""Interface for actions in the AutoQliq framework."""

from typing import Dict, Any, Optional, List

class IAction:
    """Interface for actions that can be executed in a workflow."""

    action_type: str = "Base"

    def execute(self, driver, credential_repo=None, context=None):
        """Execute the action using the provided driver and context."""
        pass

    def validate(self) -> bool:
        """Validate the action configuration."""
        pass

    def __init__(self,
                 name: Optional[str] = None,
                 loop_type: str = "count",
                 count: Optional[int] = None,
                 list_variable_name: Optional[str] = None,
                 condition_type: Optional[str] = None,
                 selector: Optional[str] = None,
                 variable_name: Optional[str] = None,
                 expected_value: Optional[str] = None,
                 script: Optional[str] = None,
                 loop_actions: Optional[List[IAction]] = None,
                 **kwargs):
        """Initialize a LoopAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(loop_type, str) or loop_type not in self.SUPPORTED_TYPES:
             raise ValidationError(f"loop_type must be one of {self.SUPPORTED_TYPES}.", field_name="loop_type")
        self.loop_type = loop_type
        self.count = None
        self.list_variable_name = None
        self.condition_type = condition_type
        self.selector = selector
        self.variable_name = variable_name
        self.expected_value = expected_value
        self.script = script

        if self.loop_type == "count":
             if count is None: raise ValidationError("'count' required.", field_name="count")
             try: self.count = int(count); assert self.count > 0
             except: raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(list_variable_name, str) or not list_variable_name:
                  raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
             self.list_variable_name = list_variable_name
        elif self.loop_type == "while":
             if not condition_type: raise ValidationError("'condition_type' required.", field_name="condition_type")

        self.loop_actions = loop_actions or []
        if not isinstance(self.loop_actions, list) or not all(isinstance(a, IAction) for a in self.loop_actions):
             raise ValidationError("loop_actions must be list of IAction.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Loop '{self.name}' initialized with no actions.")

        logger.debug(f"{self.action_type} '{self.name}' initialized. Type: {self.loop_type}")


    def validate(self) -> bool:
        """Validate the configuration of the loop action and its nested actions."""
        super().validate()
        if self.loop_type not in self.SUPPORTED_TYPES:
            raise ValidationError(f"Unsupported loop_type: '{self.loop_type}'.", field_name="loop_type")

        if self.loop_type == "count":
            if not isinstance(self.count, int) or self.count <= 0: raise ValidationError("Positive integer 'count' required.", field_name="count")
        elif self.loop_type == "for_each":
             if not isinstance(self.list_variable_name, str) or not self.list_variable_name: raise ValidationError("Non-empty 'list_variable_name' required.", field_name="list_variable_name")
        elif self.loop_type == "while":
             if not self.condition_type or self.condition_type not in ConditionalAction.SUPPORTED_CONDITIONS: raise ValidationError(f"Invalid 'condition_type' for 'while'.", field_name="condition_type")
             if self.condition_type in ["element_present", "element_not_present"]:
                 if not isinstance(self.selector, str) or not self.selector: raise ValidationError("Selector required.", field_name="selector")
             elif self.condition_type == "variable_equals":
                 if not isinstance(self.variable_name, str) or not self.variable_name: raise ValidationError("variable_name required.", field_name="variable_name")
                 if self.expected_value is None: logger.warning(f"'while' loop '{self.name}' compares against None.")
                 elif not isinstance(self.expected_value, str): raise ValidationError("expected_value must be string or None.", field_name="expected_value")
             elif self.condition_type == "javascript_eval":
                  if not isinstance(self.script, str) or not self.script: raise ValidationError("Non-empty 'script' required.", field_name="script")

        if not isinstance(self.loop_actions, list): raise ValidationError("loop_actions must be list.", field_name="loop_actions")
        if not self.loop_actions: logger.warning(f"Validation: Loop '{self.name}' has no actions.")

        for i, action in enumerate(self.loop_actions):
            branch="loop_actions"; idx=i+1
            if not isinstance(action, IAction): raise ValidationError(f"Item {idx} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {idx} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def _evaluate_while_condition(self, driver: IWebDriver, context: Optional[Dict[str, Any]]) -> bool:
         """Evaluate the 'while' loop condition."""
         temp_cond = ConditionalAction(
              condition_type=self.condition_type or "", selector=self.selector,
              variable_name=self.variable_name, expected_value=self.expected_value, script=self.script
         )
         return temp_cond._evaluate_condition(driver, context) # Can raise ActionError(WebDriverError)

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the nested actions repeatedly based on the loop type."""
        # This action executes its children. Use local runner helper.
        logger.info(f"Executing {self.action_type} action (Name: {self.name}). Type: {self.loop_type}")
        try:
            self.validate()
            context = context or {}

            if not self.loop_actions:
                 logger.warning(f"Loop '{self.name}' has no actions. Skipping.")
                 return ActionResult.success("Loop completed (no actions).")

            iterations_executed = 0
            max_while_iterations = 1000 # Safety break

            # --- Use local runner helper for nested execution ---
            from src.core.workflow.runner import WorkflowRunner # Local import
            temp_runner = WorkflowRunner(driver, credential_repo, None, None) # No repo/stop needed

            if self.loop_type == "count":
                iterations_total = self.count or 0
                for i in range(iterations_total):
                    iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Iter {iteration_num}: "
                    logger.info(f"{iter_log_prefix}Starting.")
                    iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total})
                    # Execute block using helper - raises ActionError on failure
                    temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix)
                    iterations_executed = iteration_num
            elif self.loop_type == "for_each":
                 if not self.list_variable_name: raise ActionError("list_variable_name missing", self.name)
                 target_list = context.get(self.list_variable_name)
                 if not isinstance(target_list, list): return ActionResult.failure(f"Context var '{self.list_variable_name}' not list.")

                 iterations_total = len(target_list)
                 logger.info(f"Loop '{self.name}' starting 'for_each' over '{self.list_variable_name}' ({iterations_total} items).")
                 for i, item in enumerate(target_list):
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' Item {iteration_num}: "
                      logger.info(f"{iter_log_prefix}Starting.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num, 'loop_total': iterations_total, 'loop_item': item})
                      temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
            elif self.loop_type == "while":
                 logger.info(f"Loop '{self.name}' starting 'while' loop.")
                 i = 0
                 while i < max_while_iterations:
                      iteration_num = i + 1; iter_log_prefix = f"Loop '{self.name}' While Iter {iteration_num}: "
                      logger.debug(f"{iter_log_prefix}Evaluating condition...")
                      condition_met = self._evaluate_while_condition(driver, context) # Raises ActionError(WebDriverError)
                      if not condition_met: logger.info(f"{iter_log_prefix}Condition false. Exiting loop."); break
                      logger.info(f"{iter_log_prefix}Condition true. Starting iteration.")
                      iter_context = context.copy(); iter_context.update({'loop_index': i, 'loop_iteration': iteration_num})
                      temp_runner._execute_actions(self.loop_actions, iter_context, workflow_name=self.name, log_prefix=iter_log_prefix) # Raises ActionError
                      iterations_executed = iteration_num
                      i += 1
                 else: raise ActionError(f"While loop exceeded max iterations ({max_while_iterations}).", self.name)
            else:
                raise ActionError(f"Loop execution not implemented for type: {self.loop_type}", self.name)

            logger.info(f"Loop '{self.name}' completed successfully after {iterations_executed} iterations.")
            return ActionResult.success(f"Loop completed {iterations_executed} iterations.")

        except (ValidationError, ActionError) as e:
            msg = f"Error during loop execution '{self.name}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error in loop action '{self.name}'", self.name, self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))


    def to_dict(self) -> Dict[str, Any]:
        """Serialize the loop action and its nested actions."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "loop_type": self.loop_type,
            "loop_actions": serialize_actions(self.loop_actions),
        })
        if self.loop_type == "count": base_dict["count"] = self.count
        if self.loop_type == "for_each": base_dict["list_variable_name"] = self.list_variable_name
        if self.loop_type == "while":
             base_dict["condition_type"] = self.condition_type
             if self.condition_type in ["element_present", "element_not_present"]: base_dict["selector"] = self.selector
             elif self.condition_type == "variable_equals":
                  base_dict["variable_name"] = self.variable_name; base_dict["expected_value"] = self.expected_value
             elif self.condition_type == "javascript_eval": base_dict["script"] = self.script
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from the loop_actions list, recursively."""
        nested = []
        for action in self.loop_actions:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        detail = ""
        if self.loop_type == "count": detail = f"{self.count} times"
        elif self.loop_type == "for_each": detail = f"for each item in '{self.list_variable_name}'"
        elif self.loop_type == "while": detail = f"while {self.condition_type} (...)"
        action_count = len(self.loop_actions)
        return f"{self.action_type}: {self.name} ({detail}, {action_count} actions)"

################################################################################

########## END FILE: src/core/actions/loop_action.py ##########


########## START FILE: src/core/actions/error_handling_action.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Error Handling Action (Try/Catch) for AutoQliq."""

import logging
from typing import Dict, Any, Optional, List

# Core imports
from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult, ActionStatus
from src.core.interfaces import IAction, IWebDriver, ICredentialRepository
from src.core.exceptions import ActionError, ValidationError, AutoQliqError

logger = logging.getLogger(__name__)


class ErrorHandlingAction(ActionBase):
    """
    Action that attempts to execute a sequence of actions ('try') and
    optionally executes another sequence ('catch') if an error occurs in 'try'.

    If an error occurs in the 'try' block:
    - If a 'catch' block exists, it's executed. The ErrorHandlingAction SUCCEEDS
      if the 'catch' block completes without error (error is considered handled).
      It FAILS if the 'catch' block itself fails.
    - If no 'catch' block exists, the ErrorHandlingAction FAILS immediately,
      propagating the original error context.

    Attributes:
        try_actions (List[IAction]): Actions to attempt execution.
        catch_actions (List[IAction]): Actions to execute if an error occurs in try_actions.
        action_type (str): Static type name ("ErrorHandling").
    """
    action_type: str = "ErrorHandling"

    def __init__(self,
                 name: Optional[str] = None,
                 try_actions: Optional[List[IAction]] = None,
                 catch_actions: Optional[List[IAction]] = None,
                 **kwargs):
        """
        Initialize an ErrorHandlingAction.

        Args:
            name: Descriptive name for the action. Defaults to "ErrorHandling".
            try_actions: List of IAction objects for the 'try' block.
            catch_actions: Optional list of IAction objects for the 'catch' block.
            **kwargs: Catches potential extra parameters.
        """
        super().__init__(name or self.action_type, **kwargs)
        self.try_actions = try_actions or []
        self.catch_actions = catch_actions or []

        # Initial validation
        if not isinstance(self.try_actions, list) or not all(isinstance(a, IAction) for a in self.try_actions):
             raise ValidationError("try_actions must be a list of IAction objects.", field_name="try_actions")
        if not isinstance(self.catch_actions, list) or not all(isinstance(a, IAction) for a in self.catch_actions):
             raise ValidationError("catch_actions must be a list of IAction objects.", field_name="catch_actions")
        if not self.try_actions:
            logger.warning(f"ErrorHandling action '{self.name}' initialized with no actions in 'try' block.")

        logger.debug(f"{self.action_type} '{self.name}' initialized.")

    def validate(self) -> bool:
        """Validate the configuration and nested actions."""
        super().validate()

        # Validate nested actions
        if not self.try_actions: logger.warning(f"Validation: ErrorHandling '{self.name}' has no try_actions.")
        for i, action in enumerate(self.try_actions):
            branch = "try_actions"
            if not isinstance(action, IAction): raise ValidationError(f"Item {i+1} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {i+1} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        for i, action in enumerate(self.catch_actions):
            branch = "catch_actions"
            if not isinstance(action, IAction): raise ValidationError(f"Item {i+1} in {branch} not IAction.", field_name=f"{branch}[{i}]")
            try: action.validate()
            except ValidationError as e: raise ValidationError(f"Action {i+1} in {branch} failed validation: {e}", field_name=f"{branch}[{i}]") from e

        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute the 'try' actions, running 'catch' actions if an error occurs."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}).")
        original_error: Optional[Exception] = None
        original_failure_result: Optional[ActionResult] = None
        try_block_success = True

        # --- Execute Try Block ---
        logger.debug(f"Entering 'try' block of '{self.name}'.")
        for i, action in enumerate(self.try_actions):
            action_display = f"{action.name} ({action.action_type}, Step {i+1} in 'try')"
            logger.debug(f"Executing nested action: {action_display}")
            try:
                # Execute nested action, passing context
                nested_result = action.execute(driver, credential_repo, context)
                if not nested_result.is_success():
                    error_msg = f"Nested action '{action_display}' failed: {nested_result.message}"
                    logger.warning(error_msg) # Warning as it might be caught
                    original_failure_result = nested_result # Store the failed result
                    try_block_success = False
                    break
                logger.debug(f"Nested action '{action_display}' succeeded.")
            except Exception as e:
                error_msg = f"Exception in nested action '{action_display}': {e}"
                logger.error(error_msg, exc_info=True)
                original_error = e # Store the original exception
                try_block_success = False
                break

        # --- Execute Catch Block (if error occurred and catch exists) ---
        if not try_block_success:
            fail_reason = str(original_error or original_failure_result.message)
            logger.warning(f"'try' block of '{self.name}' failed. Reason: {fail_reason}")

            if not self.catch_actions:
                 logger.warning(f"No 'catch' block defined for '{self.name}'. Propagating failure.")
                 fail_msg = f"'try' block failed and no 'catch' block defined. Original error: {fail_reason}"
                 # Return failure, preserving original failure if possible
                 return ActionResult.failure(fail_msg)
            else:
                logger.info(f"Executing 'catch' block of '{self.name}' due to error.")
                catch_context = (context or {}).copy()
                # Add error details to context for catch block
                catch_context['try_block_error_message'] = fail_reason
                catch_context['try_block_error_type'] = type(original_error).__name__ if original_error else "ActionFailure"

                for i, catch_action in enumerate(self.catch_actions):
                     action_display = f"{catch_action.name} ({catch_action.action_type}, Step {i+1} in 'catch')"
                     logger.debug(f"Executing catch action: {action_display}")
                     try:
                         catch_result = catch_action.execute(driver, credential_repo, catch_context)
                         if not catch_result.is_success():
                              error_msg = f"Catch action '{action_display}' failed: {catch_result.message}"
                              logger.error(error_msg)
                              # If catch block fails, the whole action fails definitively
                              return ActionResult.failure(f"Original error occurred AND 'catch' block failed. Catch failure: {error_msg}")
                         logger.debug(f"Catch action '{action_display}' succeeded.")
                     except Exception as catch_e:
                          error_msg = f"Exception in catch action '{action_display}': {catch_e}"
                          logger.error(error_msg, exc_info=True)
                          # Exception in catch block also means overall failure
                          return ActionResult.failure(f"Original error occurred AND 'catch' block raised exception. Catch exception: {error_msg}")

                # If catch block completed without errors
                logger.info(f"'catch' block of '{self.name}' executed successfully after handling error.")
                # The error was "handled" by the catch block
                return ActionResult.success(f"Error handled by 'catch' block in '{self.name}'.")

        # If try block succeeded without errors
        logger.info(f"'try' block of '{self.name}' executed successfully.")
        return ActionResult.success(f"'{self.name}' executed successfully (no errors).")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error handling action and its branches."""
        from src.infrastructure.repositories.serialization.action_serializer import serialize_actions
        base_dict = super().to_dict()
        base_dict.update({
            "try_actions": serialize_actions(self.try_actions),
            "catch_actions": serialize_actions(self.catch_actions),
        })
        return base_dict

    def get_nested_actions(self) -> List[IAction]:
        """Return actions from both try and catch branches, recursively."""
        nested = []
        for action in self.try_actions + self.catch_actions:
            nested.append(action)
            nested.extend(action.get_nested_actions())
        return nested

    def __str__(self) -> str:
        """User-friendly string representation."""
        try_count = len(self.try_actions)
        catch_count = len(self.catch_actions)
        return f"{self.action_type}: {self.name} (Try: {try_count} actions, Catch: {catch_count} actions)"

########## END FILE: src/core/actions/error_handling_action.py ##########


########## START FILE: src/infrastructure/common/error_handling.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Error handling utilities for infrastructure layer."""
import functools
import logging
from typing import Any, Callable, Type, TypeVar, Tuple, Optional

# Assuming AutoQliqError and potentially other specific core errors are defined
from src.core.exceptions import AutoQliqError, RepositoryError, WebDriverError, ConfigError, SerializationError, ValidationError # Add others as needed

# Type variables for better type hinting
T = TypeVar('T') # Represents the return type of the decorated function
E = TypeVar('E', bound=AutoQliqError) # Represents the specific AutoQliqError subclass to raise

logger = logging.getLogger(__name__)

def handle_exceptions(
    error_class: Type[E],
    context_message: str,
    log_level: int = logging.ERROR,
    reraise_types: Optional[Tuple[Type[Exception], ...]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to catch exceptions, log them, and wrap them in a specified AutoQliqError subclass.

    Args:
        error_class (Type[E]): The AutoQliqError subclass to raise (e.g., RepositoryError).
        context_message (str): A descriptive message of the operation context where the error occurred.
                               This message will prefix the original error message.
        log_level (int): The logging level to use when an exception is caught (e.g., logging.ERROR).
                         Defaults to logging.ERROR.
        reraise_types (Optional[Tuple[Type[Exception], ...]]): A tuple of exception types that should be
                                                               re-raised directly without wrapping.
                                                               By default, includes AutoQliqError and its subclasses.

    Returns:
        Callable[[Callable[..., T]], Callable[..., T]]: A decorator function.
    """
    # Default types to re-raise directly: the target error_class and any AutoQliqError
    # This prevents double-wrapping of already specific domain errors.
    if reraise_types is None:
        default_reraise = (AutoQliqError,)
    else:
        # Ensure AutoQliqError is always included unless explicitly excluded
        if not any(issubclass(rt, AutoQliqError) or rt == AutoQliqError for rt in reraise_types):
             reraise_types = reraise_types + (AutoQliqError,)
        default_reraise = reraise_types


    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except default_reraise as e:
                # Re-raise specified exception types directly (includes AutoQliqError and its children by default)
                # Log it first for visibility only if it hasn't likely been logged deeper
                if log_level <= logger.getEffectiveLevel(): # Check if logging is enabled at this level
                    logger.log(log_level, f"Re-raising existing {type(e).__name__} from {func.__name__}: {e}")
                raise
            except Exception as e:
                # Format the error message including context and original error
                # Ensure cause message is included
                cause_msg = str(e) if str(e) else type(e).__name__
                formatted_msg = f"{context_message}: {type(e).__name__} - {cause_msg}"
                # Log the error with traceback for unexpected exceptions
                logger.log(log_level, f"Error in {func.__name__}: {formatted_msg}", exc_info=True)
                # Create and raise the new wrapped exception
                raise error_class(formatted_msg, cause=e) from e
        return wrapper
    return decorator

# Example Usage:
#
# from src.core.exceptions import RepositoryError
#
# @handle_exceptions(RepositoryError, "Failed to load entity from file")
# def load_from_file(file_path: str) -> dict:
#     # ... file loading logic that might raise IOError, json.JSONDecodeError etc. ...
#     pass
#
# @handle_exceptions(WebDriverError, "Failed to click element", reraise_types=(TimeoutException,)) # Reraise Timeout directly
# def click_button(selector: str):
#     # ... webdriver logic ... WebDriverError will still be re-raised directly by default
#     pass

########## END FILE: src/infrastructure/common/error_handling.py ##########


########## START FILE: src/infrastructure/common/logging_utils.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Logging utilities for infrastructure layer."""
import functools
import logging
from typing import Any, Callable, TypeVar

# Type variables for better type hinting
T = TypeVar('T') # Represents the return type of the decorated function

def log_method_call(logger: logging.Logger, level: int = logging.DEBUG, log_result: bool = True, log_args: bool = True) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to log method calls, arguments, and optionally results.

    Args:
        logger (logging.Logger): The logger instance to use.
        level (int): The logging level for call/return messages (e.g., logging.DEBUG).
                     Defaults to logging.DEBUG.
        log_result (bool): Whether to log the return value of the method.
                           Defaults to True. Be cautious with sensitive data.
        log_args (bool): Whether to log the arguments passed to the method.
                         Defaults to True. Be cautious with sensitive data.

    Returns:
        Callable[[Callable[..., T]], Callable[..., T]]: A decorator function.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # --- Format Call Info ---
            func_name = func.__name__
            # Check if it's a method (first arg is likely 'self' or 'cls')
            is_method = args and hasattr(args[0], func_name) and callable(getattr(args[0], func_name))
            class_name = args[0].__class__.__name__ if is_method else ""
            full_name = f"{class_name}.{func_name}" if class_name else func_name

            # --- Format Arguments (if requested) ---
            signature = ""
            if log_args:
                start_index = 1 if is_method else 0
                try:
                    # Represent args, handle potential large objects or sensitive data if needed
                    # Be very careful logging args in production if they contain sensitive info
                    args_repr = [repr(a) for a in args[start_index:]]
                except Exception:
                    args_repr = ["<error representing args>"]

                try:
                    kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                except Exception:
                    kwargs_repr = ["<error representing kwargs>"]

                # Combine args and kwargs
                signature_parts = args_repr + kwargs_repr
                # Truncate long signatures
                max_sig_len = 250
                temp_signature = ", ".join(signature_parts)
                if len(temp_signature) > max_sig_len:
                    signature = temp_signature[:max_sig_len] + "..."
                else:
                    signature = temp_signature

            # --- Log Entry ---
            if log_args:
                logger.log(level, f"Calling: {full_name}({signature})")
            else:
                logger.log(level, f"Calling: {full_name}(...)")


            # --- Execute Original Function ---
            try:
                result = func(*args, **kwargs)
                # --- Log Exit/Result ---
                result_repr = ""
                if log_result:
                    try:
                        # Represent result, handle potential large objects or sensitive data
                        result_repr = repr(result)
                        # Truncate long results if necessary
                        max_repr_len = 200
                        if len(result_repr) > max_repr_len:
                            result_repr = result_repr[:max_repr_len] + "..."
                        result_repr = f" -> {result_repr}" # Add arrow only if logging result
                    except Exception:
                        result_repr = " -> <error representing result>"

                logger.log(level, f"Finished: {full_name}{result_repr}")
                return result
            except Exception as e:
                # --- Log Exception ---
                # Log full traceback for errors
                log_level_exc = logging.ERROR if level < logging.ERROR else level
                logger.log(log_level_exc, f"Exception in {full_name}: {type(e).__name__} - {e}", exc_info=True)
                raise # Re-raise the exception after logging
        return wrapper
    return decorator

# Example Usage:
#
# logger = logging.getLogger(__name__)
#
# class MyClass:
#     @log_method_call(logger)
#     def process_data(self, data: dict, factor: int = 2) -> str:
#         # ... processing ...
#         return f"Processed {len(data)} items with factor {factor}"
#
# instance = MyClass()
# instance.process_data({"a": 1, "b": 2}, factor=3)

########## END FILE: src/infrastructure/common/logging_utils.py ##########


########## START FILE: src/ui/common/ui_factory.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""UI factory for creating common UI components."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any, Optional, Union

from src.core.exceptions import UIError


class UIFactory:
    """Factory for creating common UI components.

    This class provides methods for creating common UI components with consistent
    styling and behavior. It primarily uses ttk widgets for a modern look.
    """

    @staticmethod
    def create_frame(parent: tk.Widget, padding: Union[str, int] = "10", relief: str = tk.FLAT, **kwargs) -> ttk.Frame:
        """Create a frame with consistent styling.

        Args:
            parent: The parent widget.
            padding: The padding to apply to the frame (e.g., "10" or 10 or "5 10").
            relief: Border style (e.g., tk.FLAT, tk.RAISED, tk.SUNKEN, tk.GROOVE).
            **kwargs: Additional ttk.Frame options.

        Returns:
            A configured ttk.Frame.

        Raises:
            UIError: If the frame cannot be created.
        """
        try:
            frame = ttk.Frame(parent, padding=padding, relief=relief, **kwargs)
            return frame
        except Exception as e:
            error_msg = "Failed to create frame"
            raise UIError(error_msg, component_name="Frame", cause=e) from e

    @staticmethod
    def create_label_frame(parent: tk.Widget, text: str, padding: Union[str, int] = "10", **kwargs) -> ttk.LabelFrame:
        """Create a labeled frame with consistent styling.

        Args:
            parent: The parent widget.
            text: The text label for the frame.
            padding: The padding to apply inside the frame.
            **kwargs: Additional ttk.LabelFrame options.

        Returns:
            A configured ttk.LabelFrame.

        Raises:
            UIError: If the labeled frame cannot be created.
        """
        try:
            frame = ttk.LabelFrame(parent, text=text, padding=padding, **kwargs)
            return frame
        except Exception as e:
            error_msg = f"Failed to create labeled frame: {text}"
            raise UIError(error_msg, component_name="LabelFrame", cause=e) from e

    @staticmethod
    def create_button(
        parent: tk.Widget,
        text: str,
        command: Optional[Callable[[], None]] = None, # Allow None command
        width: Optional[int] = None,
        state: str = tk.NORMAL,
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Button:
        """Create a button with consistent styling.

        Args:
            parent: The parent widget.
            text: The text to display on the button.
            command: The callback to execute when the button is clicked.
            width: The width of the button in characters (approximate).
            state: The initial state of the button (tk.NORMAL, tk.DISABLED).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Button options.

        Returns:
            A configured ttk.Button.

        Raises:
            UIError: If the button cannot be created.
        """
        try:
            button = ttk.Button(parent, text=text, command=command, width=width, state=state, style=style, **kwargs)
            return button
        except Exception as e:
            error_msg = f"Failed to create button: {text}"
            raise UIError(error_msg, component_name="Button", cause=e) from e

    @staticmethod
    def create_label(
        parent: tk.Widget,
        text: str = "",
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        anchor: str = tk.W, # Default to west alignment
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Label:
        """Create a label with consistent styling.

        Args:
            parent: The parent widget.
            text: The static text to display (if textvariable is None).
            textvariable: The variable to bind to the label's text.
            width: The width of the label in characters (approximate).
            anchor: How the text is positioned within the label space (e.g., tk.W, tk.CENTER).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Label options.

        Returns:
            A configured ttk.Label.

        Raises:
            UIError: If the label cannot be created.
        """
        try:
            label = ttk.Label(parent, text=text, textvariable=textvariable, width=width, anchor=anchor, style=style, **kwargs)
            return label
        except Exception as e:
            error_msg = f"Failed to create label: {text or textvariable}"
            raise UIError(error_msg, component_name="Label", cause=e) from e

    @staticmethod
    def create_entry(
        parent: tk.Widget,
        textvariable: Optional[tk.StringVar] = None,
        width: Optional[int] = None,
        state: str = tk.NORMAL,
        show: Optional[str] = None, # For password fields
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Entry:
        """Create an entry with consistent styling.

        Args:
            parent: The parent widget.
            textvariable: The variable to bind to the entry.
            width: The width of the entry in characters (approximate).
            state: The initial state of the entry (tk.NORMAL, tk.DISABLED, "readonly").
            show: Character to display instead of actual input (e.g., "*").
            style: Optional ttk style name.
            **kwargs: Additional ttk.Entry options.

        Returns:
            A configured ttk.Entry.

        Raises:
            UIError: If the entry cannot be created.
        """
        try:
            entry = ttk.Entry(parent, textvariable=textvariable, width=width, state=state, show=show, style=style, **kwargs)
            return entry
        except Exception as e:
            error_msg = "Failed to create entry"
            raise UIError(error_msg, component_name="Entry", cause=e) from e

    @staticmethod
    def create_combobox(
        parent: tk.Widget,
        textvariable: Optional[tk.StringVar] = None,
        values: Optional[List[str]] = None,
        width: Optional[int] = None,
        state: str = "readonly", # Default to readonly to prevent typing arbitrary text
        style: Optional[str] = None,
        **kwargs
    ) -> ttk.Combobox:
        """Create a combobox with consistent styling.

        Args:
            parent: The parent widget.
            textvariable: The variable to bind to the combobox.
            values: The list of values to display in the dropdown.
            width: The width of the combobox in characters (approximate).
            state: The initial state ('readonly', tk.NORMAL, tk.DISABLED).
            style: Optional ttk style name.
            **kwargs: Additional ttk.Combobox options.

        Returns:
            A configured ttk.Combobox.

        Raises:
            UIError: If the combobox cannot be created.
        """
        try:
            combobox = ttk.Combobox(
                parent,
                textvariable=textvariable,
                values=values or [],
                width=width,
                state=state,
                style=style,
                **kwargs
            )
            return combobox
        except Exception as e:
            error_msg = "Failed to create combobox"
            raise UIError(error_msg, component_name="Combobox", cause=e) from e

    @staticmethod
    def create_listbox(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.BROWSE, # BROWSE is often better default than SINGLE
        **kwargs
    ) -> tk.Listbox:
        """Create a listbox (using standard tk for better compatibility).

        Args:
            parent: The parent widget.
            height: The height of the listbox in lines.
            width: The width of the listbox in characters (approximate).
            selectmode: The selection mode (tk.SINGLE, tk.BROWSE, tk.MULTIPLE, tk.EXTENDED).
            **kwargs: Additional tk.Listbox options.

        Returns:
            A configured tk.Listbox.

        Raises:
            UIError: If the listbox cannot be created.
        """
        try:
            listbox = tk.Listbox(parent, height=height, width=width, selectmode=selectmode, **kwargs)
            # Consider adding borderwidth=0 if using inside ttk.Frame to avoid double borders
            # listbox.config(borderwidth=0, highlightthickness=0) # Example
            return listbox
        except Exception as e:
            error_msg = "Failed to create listbox"
            raise UIError(error_msg, component_name="Listbox", cause=e) from e

    @staticmethod
    def create_scrollbar(
        parent: tk.Widget,
        orient: str = tk.VERTICAL,
        command: Optional[Callable] = None
    ) -> ttk.Scrollbar:
        """Create a scrollbar with consistent styling.

        Args:
            parent: The parent widget.
            orient: The orientation (tk.VERTICAL or tk.HORIZONTAL).
            command: The command to execute when the scrollbar is moved (e.g., listbox.yview).

        Returns:
            A configured ttk.Scrollbar.

        Raises:
            UIError: If the scrollbar cannot be created.
        """
        try:
            scrollbar = ttk.Scrollbar(parent, orient=orient, command=command)
            return scrollbar
        except Exception as e:
            error_msg = "Failed to create scrollbar"
            raise UIError(error_msg, component_name="Scrollbar", cause=e) from e

    @staticmethod
    def create_text(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL,
        **kwargs
    ) -> tk.Text:
        """Create a text widget (using standard tk).

        Args:
            parent: The parent widget.
            height: The height of the text widget in lines.
            width: The width of the text widget in characters (approximate).
            wrap: The wrap mode (tk.WORD, tk.CHAR, tk.NONE).
            state: The initial state (tk.NORMAL, tk.DISABLED).
            **kwargs: Additional tk.Text options.

        Returns:
            A configured tk.Text widget.

        Raises:
            UIError: If the text widget cannot be created.
        """
        try:
            text = tk.Text(parent, height=height, width=width, wrap=wrap, state=state, **kwargs)
            # text.config(borderwidth=0, highlightthickness=0) # Optional styling
            return text
        except Exception as e:
            error_msg = "Failed to create text widget"
            raise UIError(error_msg, component_name="Text", cause=e) from e

    @staticmethod
    def create_separator(parent: tk.Widget, orient: str = tk.HORIZONTAL, **kwargs) -> ttk.Separator:
        """Create a separator line.

        Args:
            parent: The parent widget.
            orient: Orientation (tk.HORIZONTAL or tk.VERTICAL).
            **kwargs: Additional ttk.Separator options.

        Returns:
            A configured ttk.Separator.

        Raises:
            UIError: If the separator cannot be created.
        """
        try:
            separator = ttk.Separator(parent, orient=orient, **kwargs)
            return separator
        except Exception as e:
            error_msg = "Failed to create separator"
            raise UIError(error_msg, component_name="Separator", cause=e) from e

    # --- Composite Component Creation (moved from ComponentFactory) ---

    @staticmethod
    def create_scrolled_listbox(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        selectmode: str = tk.BROWSE
    ) -> Dict[str, Union[tk.Listbox, ttk.Scrollbar, ttk.Frame]]:
        """Create a listbox with a vertical scrollbar in a frame.

        Args:
            parent: The parent widget.
            height: The height of the listbox in lines.
            width: The width of the listbox in characters.
            selectmode: The selection mode (tk.SINGLE, tk.BROWSE, etc.).

        Returns:
            A dictionary containing {'frame': ttk.Frame, 'listbox': tk.Listbox, 'scrollbar': ttk.Scrollbar}.

        Raises:
            UIError: If the scrolled listbox cannot be created.
        """
        try:
            # Use FLAT relief for the outer frame usually looks better
            frame = UIFactory.create_frame(parent, padding=0, relief=tk.SUNKEN, borderwidth=1)
            scrollbar = UIFactory.create_scrollbar(frame, orient=tk.VERTICAL)
            listbox = UIFactory.create_listbox(frame, height=height, width=width, selectmode=selectmode,
                                              yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)

            # Grid layout inside the frame is often more flexible
            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            listbox.grid(row=0, column=0, sticky=tk.NSEW)
            scrollbar.grid(row=0, column=1, sticky=tk.NS)

            return {"frame": frame, "listbox": listbox, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled listbox"
            raise UIError(error_msg, component_name="ScrolledListbox", cause=e) from e

    @staticmethod
    def create_scrolled_text(
        parent: tk.Widget,
        height: int = 10,
        width: int = 50,
        wrap: str = tk.WORD,
        state: str = tk.NORMAL,
        **text_kwargs
    ) -> Dict[str, Union[tk.Text, ttk.Scrollbar, ttk.Frame]]:
        """Create a text widget with a vertical scrollbar in a frame.

        Args:
            parent: The parent widget.
            height: The height of the text widget in lines.
            width: The width of the text widget in characters.
            wrap: The wrap mode (tk.WORD, tk.CHAR, tk.NONE).
            state: The initial state (tk.NORMAL, tk.DISABLED).
            **text_kwargs: Additional keyword arguments for the tk.Text widget.

        Returns:
            A dictionary containing {'frame': ttk.Frame, 'text': tk.Text, 'scrollbar': ttk.Scrollbar}.

        Raises:
            UIError: If the scrolled text widget cannot be created.
        """
        try:
            frame = UIFactory.create_frame(parent, padding=0, relief=tk.SUNKEN, borderwidth=1)
            scrollbar = UIFactory.create_scrollbar(frame, orient=tk.VERTICAL)
            text = UIFactory.create_text(frame, height=height, width=width, wrap=wrap, state=state,
                                        yscrollcommand=scrollbar.set, **text_kwargs)
            scrollbar.config(command=text.yview)

            frame.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            text.grid(row=0, column=0, sticky=tk.NSEW)
            scrollbar.grid(row=0, column=1, sticky=tk.NS)

            return {"frame": frame, "text": text, "scrollbar": scrollbar}
        except Exception as e:
            error_msg = "Failed to create scrolled text widget"
            raise UIError(error_msg, component_name="ScrolledText", cause=e) from e

########## END FILE: src/ui/common/ui_factory.py ##########


########## START FILE: src/ui/dialogs/action_editor_dialog.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Custom dialog for adding/editing workflow actions."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, List

from src.core.exceptions import ValidationError, UIError, ActionError
from src.core.actions.factory import ActionFactory # To get action types and create for validation
from src.ui.common.ui_factory import UIFactory
# Assuming Action parameter specs are defined or accessible
# For now, use the hardcoded spec within this file.
# from .action_param_specs import ACTION_PARAMS # Ideal approach

logger = logging.getLogger(__name__)

class ActionEditorDialog(tk.Toplevel):
    """
    A modal dialog window for creating or editing workflow action parameters.
    Dynamically displays input fields based on the selected action type.
    Includes improved validation feedback.
    """
    # Define parameter specs for each action type
    # Format: { 'param_key': {'label': 'Label Text', 'widget': 'widget_type', 'options': {<widget_options>}, 'required': bool, 'tooltip': '...' } }
    # Widget Types: 'entry', 'combobox', 'entry_with_browse', 'label_readonly', 'number_entry' (future), 'checkbox' (future)
    ACTION_PARAMS = {
        # ActionBase params (handled separately) - "name"
        "Navigate": {
            "url": {"label": "URL:", "widget": "entry", "required": True, "tooltip": "Full URL (e.g., https://example.com)"}
        },
        "Click": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the element"}
        },
        "Type": {
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": True, "tooltip": "CSS selector for the input field"},
            "value_type": {"label": "Value Type:", "widget": "combobox", "required": True, "options": {"values": ["text", "credential"]}, "tooltip": "Source of the text"},
            "value_key": {"label": "Text / Key:", "widget": "entry", "required": True, "tooltip": "Literal text or credential key (e.g., login.username)"}
        },
        "Wait": {
            "duration_seconds": {"label": "Duration (sec):", "widget": "entry", "required": True, "options": {"width": 10}, "tooltip": "Pause time in seconds (e.g., 1.5)"}
        },
        "Screenshot": {
            "file_path": {"label": "File Path:", "widget": "entry_with_browse", "required": True, "options": {"browse_type": "save_as"}, "tooltip": "Path to save the PNG file"}
        },
        "Conditional": {
            "condition_type": {"label": "Condition:", "widget": "combobox", "required": True, "options": {"values": ["element_present", "element_not_present", "variable_equals"]}, "tooltip": "Condition to evaluate"},
            "selector": {"label": "CSS Selector:", "widget": "entry", "required": False, "tooltip": "Required for element conditions"}, # Required conditionally
            "variable_name": {"label": "Variable Name:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "expected_value": {"label": "Expected Value:", "widget": "entry", "required": False, "tooltip": "Required for variable conditions"},
            "true_branch": {"label": "True Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
            "false_branch": {"label": "False Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Loop": {
            "loop_type": {"label": "Loop Type:", "widget": "combobox", "required": True, "options": {"values": ["count", "for_each"]}, "tooltip": "Type of loop"},
            "count": {"label": "Iterations:", "widget": "entry", "required": False, "options": {"width": 10}, "tooltip": "Required for 'count' loop"},
            "list_variable_name": {"label": "List Variable:", "widget": "entry", "required": False, "tooltip": "Context variable name holding list for 'for_each'"},
            "loop_actions": {"label": "Loop Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "ErrorHandling": {
             "try_actions": {"label": "Try Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"},
             "catch_actions": {"label": "Catch Actions:", "widget": "label_readonly", "required": False, "tooltip": "Edit in main list"}
        },
        "Template": {
            "template_name": {"label": "Template Name:", "widget": "entry", "required": True, "tooltip": "Name of the saved template to execute"}
        }
        # Add new action types and their parameters here
    }


    def __init__(self, parent: tk.Widget, initial_data: Optional[Dict[str, Any]] = None):
        """Initialize the Action Editor Dialog."""
        super().__init__(parent)
        self.parent = parent
        self.initial_data = initial_data or {}
        self.result: Optional[Dict[str, Any]] = None

        self.is_edit_mode = bool(initial_data)
        self.title("Edit Action" if self.is_edit_mode else "Add Action")

        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self._action_type_var = tk.StringVar(self)
        # Stores {'param_key': {'label': Label, 'widget': Widget, 'var': StringVar/IntVar, 'frame': Frame (optional)}}
        self._param_widgets: Dict[str, Dict[str, Any]] = {}
        self._param_frame: Optional[ttk.Frame] = None

        try:
            self._create_widgets()
            self._populate_initial_data()
        except Exception as e:
            logger.exception("Failed to create ActionEditorDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize action editor: {e}", parent=parent)
            self.destroy()
            return # Exit init if UI fails

        self.grab_set() # Make modal AFTER widgets potentially created
        self._center_window()
        # Don't call wait_window here; call show() externally


    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # --- Action Type ---
        row = 0
        UIFactory.create_label(main_frame, text="Action Type:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        action_types = ActionFactory.get_registered_action_types()
        if not action_types: raise UIError("No action types registered.")

        self.type_combobox = UIFactory.create_combobox(
            main_frame, textvariable=self._action_type_var, values=action_types, state="readonly", width=48
        )
        self.type_combobox.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
        # Set initial type before trace, otherwise trace runs with default empty value first
        initial_type = self.initial_data.get("type", action_types[0])
        if initial_type not in action_types: initial_type = action_types[0]
        self._action_type_var.set(initial_type)
        self._action_type_var.trace_add("write", self._on_type_change)

        # --- Action Name ---
        row += 1
        # Use helper to create + store name widget references
        self._create_parameter_widget(main_frame, "name", "Action Name:", "entry", row=row, options={'width': 50})

        # --- Dynamic Parameter Frame ---
        row += 1
        self._param_frame = UIFactory.create_label_frame(main_frame, text="Parameters")
        self._param_frame.grid(row=row, column=0, columnspan=2, sticky=tk.NSEW, pady=10)
        self._param_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        row += 1
        button_frame = UIFactory.create_frame(main_frame, padding="5 0 0 0")
        button_frame.grid(row=row, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))

        cancel_button = UIFactory.create_button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        ok_button = UIFactory.create_button(button_frame, text="OK", command=self._on_ok)
        ok_button.pack(side=tk.RIGHT)
        self.bind('<Return>', lambda e: self._on_ok())
        self.bind('<Escape>', lambda e: self._on_cancel())

    def _populate_initial_data(self):
        """Fill fields with initial data if in edit mode."""
        # Name is populated separately
        name_var = self._param_widgets.get("name", {}).get("var")
        if name_var:
             # Use initial name if present, otherwise default to action type
             name_val = self.initial_data.get("name", self._action_type_var.get())
             name_var.set(name_val)

        # Populate dynamic fields based on current (initial) type
        self._update_parameter_fields() # This will now populate values for the initial type


    def _on_type_change(self, *args):
        """Callback when the action type combobox value changes."""
        action_type = self._action_type_var.get()
        # Update default name if name hasn't been manually changed
        name_var = self._param_widgets["name"]["var"]
        current_name = name_var.get()
        registered_types = ActionFactory.get_registered_action_types()
        if current_name in registered_types or not current_name: # Update if default or empty
             name_var.set(action_type)

        self._update_parameter_fields() # Regenerate fields for new type

    def _update_parameter_fields(self):
        """Clear and recreate parameter widgets based on selected action type."""
        if not self._param_frame: return
        action_type = self._action_type_var.get()
        logger.debug(f"Updating parameters for action type: {action_type}")

        # Clear existing dynamic widgets
        for widget in self._param_frame.winfo_children(): widget.destroy()
        # Clear non-name entries from _param_widgets dict
        keys_to_delete = [k for k in self._param_widgets if k != 'name']
        for key in keys_to_delete: del self._param_widgets[key]

        # --- Create Fields for Selected Action Type ---
        param_specs = self.ACTION_PARAMS.get(action_type, {})
        row = 0
        for key, spec in param_specs.items():
            initial_val = self.initial_data.get(key) if self.is_edit_mode else None
            # Create widget using helper, which now handles initial value setting
            self._create_parameter_widget(
                self._param_frame, key,
                spec.get("label", key.replace('_', ' ').title() + ":"),
                spec.get("widget", "entry"),
                row=row, options=spec.get("options", {}), initial_value=initial_val
            )
            row += 1

    def _create_parameter_widget(self, parent: tk.Widget, key: str, label_text: str, widget_type: str, row: int, options: Optional[Dict]=None, initial_value: Optional[Any]=None):
        """Helper to create label, input widget, store references, and set initial value."""
        options = options or {}
        var: Optional[tk.Variable] = None
        widget: Optional[tk.Widget] = None
        browse_btn: Optional[tk.Widget] = None
        width = options.get('width', 40)

        # Determine variable type and create var
        # Add more types like BooleanVar if Checkbox is used
        var = tk.StringVar(self)
        self._param_widgets[key] = {'label': None, 'widget': None, 'var': var, 'browse_btn': None} # Store var first

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        self._param_widgets[key]['label'] = label

        # Create widget
        widget_frame_needed = widget_type == "entry_with_browse"
        container = UIFactory.create_frame(parent, padding=0) if widget_frame_needed else parent

        if widget_type == "entry":
             widget = UIFactory.create_entry(container, textvariable=var, width=width, **options.get('config', {}))
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  container, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width-2
             )
        elif widget_type == "entry_with_browse":
             entry_frame = container # Use the frame created above
             entry_frame.columnconfigure(0, weight=1)
             widget = UIFactory.create_entry(entry_frame, textvariable=var, width=width-5)
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda k=key, btype=browse_type: self._browse_for_path(k, btype)
             browse_btn = UIFactory.create_button(entry_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
             widget = entry_frame # Main widget for grid placement is the frame
        elif widget_type == "label_readonly":
             display_text = ""
             if initial_value is not None and isinstance(initial_value, list):
                  display_text = f"({len(initial_value)} actions, edit in main list)"
             else:
                  display_text = str(initial_value) if initial_value is not None else "(Not editable)"
             var.set(display_text)
             widget = UIFactory.create_label(container, textvariable=var, anchor=tk.W, relief=tk.SUNKEN, borderwidth=1, padding=(3,1))
        # Add other widget types here

        # Grid the widget/container
        if widget:
            grid_target = container if widget_frame_needed else widget
            grid_target.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
            self._param_widgets[key]['widget'] = widget
            self._param_widgets[key]['browse_btn'] = browse_btn

        # Set initial value *after* widget creation
        if initial_value is not None and widget_type != "label_readonly":
             try: var.set(str(initial_value))
             except tk.TclError as e: logger.warning(f"Could not set initial value for '{key}': {e}")


    def _browse_for_path(self, setting_key: str, browse_type: str):
         """Handles browsing for file or directory for a parameter field."""
         if setting_key not in self._param_widgets: return
         var = self._param_widgets[setting_key]['var']
         current_path = var.get()
         initial_dir = os.path.abspath(".")
         if current_path:
              potential_dir = os.path.dirname(current_path)
              if os.path.isdir(potential_dir): initial_dir = potential_dir
              elif os.path.isfile(current_path): initial_dir = os.path.dirname(current_path)

         new_path: Optional[str] = None
         parent_window = self # Use dialog as parent
         try:
              if browse_type == "directory": new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory", parent=parent_window)
              elif browse_type == "open": new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File", parent=parent_window)
              elif browse_type == "save_as": new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File Path", parent=parent_window)

              if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
              else: logger.debug(f"Browse cancelled for {setting_key}")
         except Exception as e:
              logger.error(f"Error during file dialog browse: {e}", exc_info=True)
              messagebox.showerror("Browse Error", f"Could not open file dialog: {e}", parent=self)

    def _on_ok(self):
        """Validate data using ActionFactory/Action.validate and close dialog."""
        action_data = {"type": self._action_type_var.get()}
        validation_errors = {}
        action_params_spec = self.ACTION_PARAMS.get(action_data["type"], {})

        # Collect data and perform basic type conversion
        for key, widgets in self._param_widgets.items():
            spec = action_params_spec.get(key, {})
            widget_type = spec.get('widget', 'entry')

            if widget_type == "label_readonly": # Skip read-only display fields
                # Keep original nested data if editing, otherwise empty list
                action_data[key] = self.initial_data.get(key, []) if self.is_edit_mode else []
                continue

            try:
                value_str = widgets["var"].get()
                value: Any = value_str # Start as string

                # Attempt type conversion based on known param names or hints
                if key == "count":
                     try: value = int(value_str) if value_str else None # Allow empty count? No, validation handles it.
                     except (ValueError, TypeError): validation_errors[key] = "Iterations must be an integer."
                elif key == "duration_seconds":
                     try: value = float(value_str) if value_str else None
                     except (ValueError, TypeError): validation_errors[key] = "Duration must be a number."
                # Add boolean conversion if checkbox is added

                action_data[key] = value # Store potentially converted value

            except Exception as e:
                 logger.error(f"Error retrieving value for param '{key}': {e}")
                 validation_errors[key] = "Error retrieving value."

        if validation_errors:
             error_msg = "Input Errors:\n\n" + "\n".join([f"- {k}: {v}" for k, v in validation_errors.items()])
             messagebox.showerror("Validation Failed", error_msg, parent=self)
             return

        # --- Final validation using ActionFactory and Action's validate() ---
        try:
            # Create temporary instance to run validation
            temp_action = ActionFactory.create_action(action_data)
            temp_action.validate() # This should raise ValidationError if invalid
            logger.debug("Action data validated successfully using action class.")
            # If valid, set result and close
            self.result = action_data
            self.destroy()
        except ValidationError as e:
             logger.warning(f"Action validation failed: {e}. Data: {action_data}")
             # Display the specific validation error message from the action
             messagebox.showerror("Validation Failed", f"Invalid action parameters:\n\n{e}", parent=self)
        except (ActionError, TypeError) as e: # Catch factory errors too
             logger.error(f"Action creation/validation failed: {e}. Data: {action_data}")
             messagebox.showerror("Validation Failed", f"Could not validate action:\n\n{e}", parent=self)
        except Exception as e:
             logger.error(f"Unexpected error validating action: {e}. Data: {action_data}", exc_info=True)
             messagebox.showerror("Validation Error", f"Unexpected error validating action:\n\n{e}", parent=self)

    def _on_cancel(self):
        """Close the dialog without setting a result."""
        self.result = None
        self.destroy()

    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_win = self.parent.winfo_toplevel()
        parent_x = parent_win.winfo_rootx(); parent_y = parent_win.winfo_rooty()
        parent_w = parent_win.winfo_width(); parent_h = parent_win.winfo_height()
        win_w = self.winfo_reqwidth(); win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth(); screen_h = self.winfo_screenheight()
        pos_x = max(0, min(pos_x, screen_w - win_w)); pos_y = max(0, min(pos_y, screen_h - win_h))
        self.geometry(f"+{pos_x}+{pos_y}")


    def show(self) -> Optional[Dict[str, Any]]:
        """Make the dialog visible and wait for user interaction."""
        self.wait_window() # Blocks until destroy() is called
        return self.result

########## END FILE: src/ui/dialogs/action_editor_dialog.py ##########


########## START FILE: src/ui/dialogs/credential_manager_dialog.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Custom dialog for managing credentials."""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Any, List

# Core imports
from src.core.exceptions import CredentialError, ValidationError, UIError
from src.core.interfaces.service import ICredentialService
# UI imports
from src.ui.common.ui_factory import UIFactory

logger = logging.getLogger(__name__)

class CredentialManagerDialog(tk.Toplevel):
    """
    A modal dialog window for listing, adding, and deleting credentials.
    Interacts with the ICredentialService.
    """

    def __init__(self, parent: tk.Widget, credential_service: ICredentialService):
        """
        Initialize the Credential Manager Dialog.

        Args:
            parent: The parent widget.
            credential_service: The service used to manage credentials.
        """
        super().__init__(parent)
        self.parent = parent
        self.credential_service = credential_service

        self.title("Manage Credentials")
        self.resizable(False, False)
        self.transient(parent) # Keep on top of parent
        self.protocol("WM_DELETE_WINDOW", self._on_close) # Handle window close

        # --- Internal State ---
        self._name_var = tk.StringVar(self)
        self._username_var = tk.StringVar(self)
        self._password_var = tk.StringVar(self)
        self._listbox: Optional[tk.Listbox] = None

        # --- Build UI ---
        try:
            self._create_widgets()
            self._load_credentials() # Initial population
        except Exception as e:
            logger.exception("Failed to create CredentialManagerDialog UI.")
            messagebox.showerror("Dialog Error", f"Failed to initialize credential manager: {e}", parent=parent)
            self.destroy()
            return # Stop further execution if init fails

        self.grab_set() # Make modal AFTER widgets are created
        self._center_window()
        self.wait_window() # Block until destroyed


    def _create_widgets(self):
        """Create the widgets for the dialog."""
        main_frame = UIFactory.create_frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1) # Listbox expands

        # --- Add/Edit Form ---
        form_frame = UIFactory.create_label_frame(main_frame, text="Add/Edit Credential")
        form_frame.grid(row=0, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        form_frame.columnconfigure(1, weight=1)

        UIFactory.create_label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        name_entry = UIFactory.create_entry(form_frame, textvariable=self._name_var)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        UIFactory.create_label(form_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        user_entry = UIFactory.create_entry(form_frame, textvariable=self._username_var)
        user_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        UIFactory.create_label(form_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        pass_entry = UIFactory.create_entry(form_frame, textvariable=self._password_var, show="*")
        pass_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)

        add_button = UIFactory.create_button(form_frame, text="Add/Update", command=self._on_add_update)
        add_button.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)
        clear_button = UIFactory.create_button(form_frame, text="Clear Fields", command=self._clear_fields)
        clear_button.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)

        # --- Credential List ---
        list_frame = UIFactory.create_label_frame(main_frame, text="Existing Credentials")
        list_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        list_scrolled = UIFactory.create_scrolled_listbox(list_frame, height=8, selectmode=tk.BROWSE)
        self._listbox = list_scrolled["listbox"]
        list_scrolled["frame"].grid(row=0, column=0, sticky=tk.NSEW)
        self._listbox.bind("<<ListboxSelect>>", self._on_list_select)

        # --- List Buttons ---
        list_button_frame = UIFactory.create_frame(main_frame)
        list_button_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)

        delete_button = UIFactory.create_button(list_button_frame, text="Delete Selected", command=self._on_delete)
        delete_button.pack(pady=5)

        close_button = UIFactory.create_button(list_button_frame, text="Close", command=self._on_close)
        close_button.pack(pady=5, side=tk.BOTTOM) # Place Close at the bottom


    def _load_credentials(self):
        """Load credential names from the service and populate the listbox."""
        if not self._listbox: return
        try:
             self._listbox.delete(0, tk.END) # Clear existing items
             credential_names = self.credential_service.list_credentials()
             for name in sorted(credential_names):
                  self._listbox.insert(tk.END, name)
             logger.debug(f"Loaded {len(credential_names)} credentials into list.")
        except Exception as e:
             logger.error(f"Failed to load credentials into dialog: {e}", exc_info=True)
             messagebox.showerror("Load Error", f"Could not load credentials: {e}", parent=self)

    def _on_list_select(self, event: Optional[tk.Event] = None):
        """Handle selection change in the listbox to populate edit fields."""
        if not self._listbox: return
        selection_indices = self._listbox.curselection()
        if not selection_indices:
            self._clear_fields() # Clear fields if nothing selected
            return

        selected_name = self._listbox.get(selection_indices[0])
        try:
            # Fetch details - WARNING: This retrieves the HASH, not the original password.
            # Editing requires re-entering the password.
            cred_details = self.credential_service.get_credential(selected_name)
            if cred_details:
                self._name_var.set(cred_details.get("name", ""))
                self._username_var.set(cred_details.get("username", ""))
                # DO NOT set the password field with the hash. Leave it blank for editing.
                self._password_var.set("")
                logger.debug(f"Populated fields for editing '{selected_name}' (password field cleared).")
            else:
                 logger.warning(f"Selected credential '{selected_name}' not found by service.")
                 self._clear_fields()
        except Exception as e:
            logger.error(f"Failed to get details for credential '{selected_name}': {e}", exc_info=True)
            messagebox.showerror("Load Error", f"Could not load details for '{selected_name}': {e}", parent=self)
            self._clear_fields()


    def _clear_fields(self):
        """Clear the input fields."""
        self._name_var.set("")
        self._username_var.set("")
        self._password_var.set("")
        # Deselect listbox item if needed
        if self._listbox: self._listbox.selection_clear(0, tk.END)
        logger.debug("Credential input fields cleared.")

    def _on_add_update(self):
        """Handle Add/Update button click."""
        name = self._name_var.get().strip()
        username = self._username_var.get().strip()
        password = self._password_var.get() # Get password as entered

        if not name or not username or not password:
            messagebox.showerror("Input Error", "Name, Username, and Password cannot be empty.", parent=self)
            return

        try:
            # Check if it exists (for logging/confirmation message)
            # exists = self.credential_service.get_credential(name) is not None
            # Service's create_credential should handle "already exists" error if needed,
            # or we assume save() in repo handles UPSERT. Let's rely on create failing if needed.

            # Attempt to create/update via service (which handles hashing)
            # A combined save/update method in the service might be cleaner.
            # For now, try create, if fails assume update? No, better to use repo UPSERT.
            # Let's assume service needs explicit create/update or repo handles UPSERT.
            # Assuming repo handles UPSERT via save()
            self.credential_service.create_credential(name, username, password) # This might fail if exists
            # Or use a save method if available in service/repo that does UPSERT logic:
            # self.credential_service.save_credential({"name": name, "username": username, "password": password})

            logger.info(f"Credential '{name}' added/updated successfully.")
            messagebox.showinfo("Success", f"Credential '{name}' saved successfully.", parent=self)
            self._clear_fields()
            self._load_credentials() # Refresh list
        except (ValidationError, CredentialError, RepositoryError) as e:
             logger.error(f"Failed to save credential '{name}': {e}")
             messagebox.showerror("Save Error", f"Failed to save credential:\n{e}", parent=self)
        except Exception as e:
             logger.exception(f"Unexpected error saving credential '{name}'.")
             messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}", parent=self)


    def _on_delete(self):
        """Handle Delete Selected button click."""
        if not self._listbox: return
        selection_indices = self._listbox.curselection()
        if not selection_indices:
            messagebox.showwarning("Delete Error", "Please select a credential to delete.", parent=self)
            return

        selected_name = self._listbox.get(selection_indices[0])

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete credential '{selected_name}'?", parent=self):
            return

        try:
            deleted = self.credential_service.delete_credential(selected_name)
            if deleted:
                logger.info(f"Credential '{selected_name}' deleted.")
                messagebox.showinfo("Success", f"Credential '{selected_name}' deleted.", parent=self)
                self._clear_fields()
                self._load_credentials() # Refresh list
            else:
                # Should not happen if item was selected from list, but handle anyway
                logger.warning(f"Attempted to delete '{selected_name}' but service reported not found.")
                messagebox.showerror("Delete Error", f"Credential '{selected_name}' could not be found for deletion.", parent=self)
                self._load_credentials() # Refresh list in case of inconsistency
        except (ValidationError, CredentialError, RepositoryError) as e:
             logger.error(f"Failed to delete credential '{selected_name}': {e}")
             messagebox.showerror("Delete Error", f"Failed to delete credential:\n{e}", parent=self)
        except Exception as e:
             logger.exception(f"Unexpected error deleting credential '{selected_name}'.")
             messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n{e}", parent=self)


    def _on_close(self):
        """Handle dialog closing."""
        logger.debug("Credential Manager dialog closed.")
        self.grab_release()
        self.destroy()

    def _center_window(self):
        """Centers the dialog window on the parent."""
        self.update_idletasks()
        parent_geo = self.parent.winfo_geometry().split('+')
        parent_w = int(parent_geo[0].split('x')[0])
        parent_h = int(parent_geo[0].split('x')[1])
        parent_x = int(parent_geo[1])
        parent_y = int(parent_geo[2])
        win_w = self.winfo_reqwidth()
        win_h = self.winfo_reqheight()
        pos_x = parent_x + (parent_w // 2) - (win_w // 2)
        pos_y = parent_y + (parent_h // 2) - (win_h // 2)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if pos_x + win_w > screen_w: pos_x = screen_w - win_w
        if pos_y + win_h > screen_h: pos_y = screen_h - win_h
        if pos_x < 0: pos_x = 0
        if pos_y < 0: pos_y = 0
        self.geometry(f"+{pos_x}+{pos_y}")

########## END FILE: src/ui/dialogs/credential_manager_dialog.py ##########


########## START FILE: src/ui/views/settings_view.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Settings view implementation for AutoQliq."""

import tkinter as tk
from tkinter import ttk, filedialog
import logging
from typing import List, Dict, Any, Optional

# Core / Infrastructure
from src.core.exceptions import UIError
from src.config import RepositoryType, BrowserTypeStr # Import literals

# UI elements
from src.ui.interfaces.presenter import IPresenter # Use base presenter interface for now
from src.ui.interfaces.view import IView # Use base view interface
from src.ui.views.base_view import BaseView
from src.ui.common.ui_factory import UIFactory
# Type hint for the specific presenter
from src.ui.presenters.settings_presenter import SettingsPresenter, ISettingsView


class SettingsView(BaseView, ISettingsView):
    """
    View component for managing application settings. Allows users to view and
    modify settings stored in config.ini.
    """
    # Define allowed values for dropdowns
    REPO_TYPES: List[RepositoryType] = ["file_system", "database"]
    BROWSER_TYPES: List[BrowserTypeStr] = ["chrome", "firefox", "edge", "safari"]
    LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def __init__(self, root: tk.Widget, presenter: SettingsPresenter):
        """
        Initialize the settings view.

        Args:
            root: The parent widget (e.g., a frame in a notebook).
            presenter: The presenter handling the logic for this view.
        """
        super().__init__(root, presenter)
        self.presenter: SettingsPresenter # Type hint

        # Dictionary to hold the tk.StringVar instances for settings
        self.setting_vars: Dict[str, tk.StringVar] = {}

        try:
            self._create_widgets()
            self.logger.info("SettingsView initialized successfully.")
            # Initial population happens via presenter.initialize_view -> presenter.load_settings -> view.set_settings_values
        except Exception as e:
            error_msg = "Failed to create SettingsView widgets"
            self.logger.exception(error_msg) # Log traceback
            self.display_error("Initialization Error", f"{error_msg}: {e}")
            raise UIError(error_msg, component_name="SettingsView", cause=e) from e

    def _create_widgets(self) -> None:
        """Create the UI elements for the settings view."""
        self.logger.debug("Creating settings widgets.")
        # Use grid layout within the main_frame provided by BaseView
        content_frame = UIFactory.create_frame(self.main_frame, padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(1, weight=1) # Allow entry/path fields to expand

        row_index = 0

        # --- General Settings ---
        general_frame = UIFactory.create_label_frame(content_frame, text="General")
        general_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        general_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(general_frame, 0, "Log Level:", "log_level", "combobox", options={'values': self.LOG_LEVELS})
        self._create_setting_row(general_frame, 1, "Log File:", "log_file", "entry_with_browse", options={'browse_type': 'save_as'})

        # --- Repository Settings ---
        repo_frame = UIFactory.create_label_frame(content_frame, text="Repository")
        repo_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        repo_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(repo_frame, 0, "Storage Type:", "repository_type", "combobox", options={'values': self.REPO_TYPES})
        self._create_setting_row(repo_frame, 1, "DB Path:", "db_path", "entry_with_browse", options={'browse_type': 'save_as', 'label_note': '(Used if type=database)'})
        self._create_setting_row(repo_frame, 2, "Workflows Path:", "workflows_path", "entry_with_browse", options={'browse_type': 'directory', 'label_note': '(Used if type=file_system)'})
        self._create_setting_row(repo_frame, 3, "Credentials Path:", "credentials_path", "entry_with_browse", options={'browse_type': 'save_as', 'label_note': '(Used if type=file_system)'})

        # --- WebDriver Settings ---
        wd_frame = UIFactory.create_label_frame(content_frame, text="WebDriver")
        wd_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        wd_frame.columnconfigure(1, weight=1)
        row_index += 1

        self._create_setting_row(wd_frame, 0, "Default Browser:", "default_browser", "combobox", options={'values': self.BROWSER_TYPES})
        self._create_setting_row(wd_frame, 1, "Implicit Wait (sec):", "implicit_wait", "entry", options={'width': 5})
        self._create_setting_row(wd_frame, 2, "ChromeDriver Path:", "chrome_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 3, "GeckoDriver Path (FF):", "firefox_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})
        self._create_setting_row(wd_frame, 4, "EdgeDriver Path:", "edge_driver_path", "entry_with_browse", options={'browse_type': 'open', 'label_note': '(Optional)'})

        # --- Action Buttons ---
        row_index += 1
        button_frame = UIFactory.create_frame(content_frame, padding="10 10 0 0") # Padding top only
        button_frame.grid(row=row_index, column=0, columnspan=3, sticky=tk.E, pady=10)

        save_btn = UIFactory.create_button(button_frame, text="Save Settings", command=self._on_save)
        save_btn.pack(side=tk.RIGHT, padx=5)
        reload_btn = UIFactory.create_button(button_frame, text="Reload Settings", command=self._on_reload)
        reload_btn.pack(side=tk.RIGHT, padx=5)


        self.logger.debug("Settings widgets created.")

    def _create_setting_row(self, parent: tk.Widget, row: int, label_text: str, setting_key: str, widget_type: str, options: Optional[Dict]=None):
        """Helper to create a label and input widget for a setting."""
        options = options or {}
        var = tk.StringVar()
        self.setting_vars[setting_key] = var

        label = UIFactory.create_label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=3)
        # Add tooltip/note if provided
        if options.get('label_note'):
             # Simple way: modify label text. Better way: use a tooltip library.
             label.config(text=f"{label_text} {options['label_note']}")


        widget_frame = UIFactory.create_frame(parent, padding=0) # Frame to hold widget + potential button
        widget_frame.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=3)
        widget_frame.columnconfigure(0, weight=1) # Make widget expand

        widget: Optional[tk.Widget] = None

        width = options.get('width', 40) # Default width slightly smaller
        if widget_type == "entry":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width)
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "combobox":
             widget = UIFactory.create_combobox(
                  widget_frame, textvariable=var, values=options.get('values', []),
                  state=options.get('state', 'readonly'), width=width
             )
             widget.grid(row=0, column=0, sticky=tk.EW)
        elif widget_type == "entry_with_browse":
             widget = UIFactory.create_entry(widget_frame, textvariable=var, width=width-5) # Adjust width for button
             widget.grid(row=0, column=0, sticky=tk.EW)
             browse_type = options.get('browse_type', 'open')
             browse_cmd = lambda key=setting_key, btype=browse_type: self._browse_for_path(key, btype)
             browse_btn = UIFactory.create_button(widget_frame, text="...", command=browse_cmd, width=3)
             browse_btn.grid(row=0, column=1, padx=(2,0))
        else:
             self.logger.error(f"Unsupported widget type '{widget_type}' for setting '{setting_key}'")


    def _browse_for_path(self, setting_key: str, browse_type: str):
        """Handles browsing for file or directory."""
        self.logger.debug(f"Browsing for path: Key={setting_key}, Type={browse_type}")
        if setting_key not in self.setting_vars: return
        var = self.setting_vars[setting_key]
        current_path = var.get()
        # Robust initial directory finding
        initial_dir = os.path.abspath(".") # Default to current dir
        if current_path:
             potential_dir = os.path.dirname(current_path)
             if os.path.isdir(potential_dir):
                  initial_dir = potential_dir
             elif os.path.isfile(current_path): # If current path is file, use its dir
                  initial_dir = os.path.dirname(current_path)

        new_path: Optional[str] = None
        parent_window = self.main_frame.winfo_toplevel() # Use toplevel as parent
        try:
             if browse_type == "directory":
                  new_path = filedialog.askdirectory(initialdir=initial_dir, title=f"Select Directory for {setting_key}", parent=parent_window)
             elif browse_type == "open":
                  new_path = filedialog.askopenfilename(initialdir=initial_dir, title=f"Select File for {setting_key}", parent=parent_window)
             elif browse_type == "save_as":
                   new_path = filedialog.asksaveasfilename(initialdir=initial_dir, initialfile=os.path.basename(current_path), title=f"Select File for {setting_key}", parent=parent_window)

             if new_path: var.set(new_path); logger.debug(f"Path selected for {setting_key}: {new_path}")
             else: logger.debug(f"Browse cancelled for {setting_key}")
        except Exception as e:
             self.logger.error(f"Error during file dialog browse: {e}", exc_info=True)
             self.display_error("Browse Error", f"Could not open file dialog: {e}")

    # --- ISettingsView Implementation ---

    def set_settings_values(self, settings: Dict[str, Any]) -> None:
        """Update the view widgets with values from the settings dictionary."""
        self.logger.debug(f"Setting settings values in view: {list(settings.keys())}")
        for key, var in self.setting_vars.items():
            if key in settings:
                 value = settings[key]
                 try: var.set(str(value) if value is not None else "") # Handle None, ensure string
                 except Exception as e: self.logger.error(f"Failed to set view variable '{key}' to '{value}': {e}")
            else:
                 self.logger.warning(f"Setting key '{key}' not found in provided settings data during set.")
                 var.set("") # Clear field if key missing from data


    def get_settings_values(self) -> Dict[str, Any]:
        """Retrieve the current values from the view widgets, attempting type conversion."""
        self.logger.debug("Getting settings values from view.")
        data = {}
        for key, var in self.setting_vars.items():
             try:
                  value_str = var.get()
                  # Attempt type conversion based on key name (heuristic)
                  if key == 'implicit_wait': data[key] = int(value_str)
                  elif key == 'repo_create_if_missing': data[key] = value_str.lower() in ['true', '1', 'yes'] # Basic bool conversion
                  else: data[key] = value_str # Keep others as strings by default
             except (ValueError, TypeError) as e:
                  self.logger.error(f"Error converting value for setting '{key}': {e}. Storing as string.")
                  data[key] = var.get() # Store as string on conversion error
             except Exception as e:
                  self.logger.error(f"Failed to get view variable for setting '{key}': {e}")
                  data[key] = None
        return data

    # --- Internal Event Handlers ---

    def _on_save(self):
        """Handle Save button click."""
        self.logger.debug("Save settings button clicked.")
        # Confirmation before potentially overwriting config.ini
        if self.confirm_action("Save Settings", "Save current settings to config.ini?\nThis may require restarting the application for some changes to take effect."):
            self.presenter.save_settings() # Delegate to presenter

    def _on_reload(self):
        """Handle Reload button click."""
        self.logger.debug("Reload settings button clicked.")
        if self.confirm_action("Reload Settings", "Discard any unsaved changes and reload settings from config.ini?"):
             self.presenter.load_settings() # Delegate reload to presenter

########## END FILE: src/ui/views/settings_view.py ##########


########## START FILE: src/ui/presenters/settings_presenter.py ##########
# GROUP: Group 2: SHOULD PROBABLY ADD

"""Presenter for the Settings View."""

import logging
from typing import Optional, Dict, Any

# Configuration manager
from src.config import AppConfig, RepositoryType, BrowserTypeStr # Import literals
from src.core.exceptions import ConfigError, ValidationError
# UI dependencies
from src.ui.interfaces.presenter import IPresenter # Base interface might suffice
from src.ui.interfaces.view import IView # Use generic view or create ISettingsView
from src.ui.presenters.base_presenter import BasePresenter

# Define a more specific interface for the Settings View if needed
class ISettingsView(IView):
    def get_settings_values(self) -> Dict[str, Any]: pass
    def set_settings_values(self, settings: Dict[str, Any]) -> None: pass
    # Add specific methods if view needs more granular updates


class SettingsPresenter(BasePresenter[ISettingsView]):
    """
    Presenter for the Settings View. Handles loading settings into the view
    and saving changes back to the configuration source (config.ini).
    """
    def __init__(self, config_manager: AppConfig, view: Optional[ISettingsView] = None):
        """
        Initialize the SettingsPresenter.

        Args:
            config_manager: The application configuration manager instance.
            view: The associated SettingsView instance.
        """
        super().__init__(view)
        if config_manager is None:
             raise ValueError("Configuration manager cannot be None.")
        self.config = config_manager
        self.logger.info("SettingsPresenter initialized.")

    def set_view(self, view: ISettingsView) -> None:
        """Set the view and load initial settings."""
        super().set_view(view)
        self.initialize_view()

    def initialize_view(self) -> None:
        """Initialize the view when it's set (calls load_settings)."""
        self.load_settings()

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Loading settings")
    def load_settings(self) -> None:
        """Load current settings from the config manager and update the view."""
        if not self.view:
             self.logger.warning("Load settings called but view is not set.")
             return

        self.logger.debug("Loading settings into view.")
        # Reload config from file to ensure latest values are shown
        self.config.reload_config()

        settings_data = {
            'log_level': logging.getLevelName(self.config.log_level),
            'log_file': self.config.log_file,
            'repository_type': self.config.repository_type,
            'workflows_path': self.config.workflows_path,
            'credentials_path': self.config.credentials_path,
            'db_path': self.config.db_path,
            'repo_create_if_missing': self.config.repo_create_if_missing,
            'default_browser': self.config.default_browser,
            'chrome_driver_path': self.config.get_driver_path('chrome') or "",
            'firefox_driver_path': self.config.get_driver_path('firefox') or "",
            'edge_driver_path': self.config.get_driver_path('edge') or "",
            'implicit_wait': self.config.implicit_wait,
            # Security settings intentionally omitted from UI editing
        }
        self.view.set_settings_values(settings_data)
        self.view.set_status("Settings loaded from config.ini.")
        self.logger.info("Settings loaded and view updated.")

    # Use decorator for methods interacting with config file I/O
    @BasePresenter.handle_errors("Saving settings")
    def save_settings(self) -> None:
        """Get settings from the view, validate, save via config manager, and reload."""
        if not self.view:
            self.logger.error("Save settings called but view is not set.")
            return

        self.logger.info("Attempting to save settings.")
        settings_to_save = self.view.get_settings_values()

        # --- Basic Validation (Presenter-level) ---
        errors = {}
        # Validate paths (basic check for emptiness if relevant)
        repo_type = settings_to_save.get('repository_type')
        if repo_type == 'file_system':
            if not settings_to_save.get('workflows_path'): errors['workflows_path'] = ["Workflows path required."]
            if not settings_to_save.get('credentials_path'): errors['credentials_path'] = ["Credentials path required."]
        elif repo_type == 'database':
             if not settings_to_save.get('db_path'): errors['db_path'] = ["Database path required."]
        else:
            errors['repository_type'] = ["Invalid repository type selected."]

        # Validate implicit wait
        try:
            wait = int(settings_to_save.get('implicit_wait', 0))
            if wait < 0: errors['implicit_wait'] = ["Implicit wait cannot be negative."]
        except (ValueError, TypeError):
            errors['implicit_wait'] = ["Implicit wait must be an integer."]
        # Validate Log Level
        log_level_str = str(settings_to_save.get('log_level', 'INFO')).upper()
        if log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
             errors['log_level'] = ["Invalid log level selected."]
        # Validate browser type
        browser_str = str(settings_to_save.get('default_browser','chrome')).lower()
        if browser_str not in ['chrome', 'firefox', 'edge', 'safari']:
             errors['default_browser'] = ["Invalid default browser selected."]


        if errors:
             self.logger.warning(f"Settings validation failed: {errors}")
             # Raise ValidationError for the decorator to catch and display
             error_msg = "Validation errors:\n" + "\n".join([f"- {field}: {err}" for field, errs in errors.items() for err in errs])
             raise ValidationError(error_msg) # Decorator will call view.display_error

        # --- Save individual settings using config manager ---
        # Wrap saving logic in try block although decorator handles file I/O errors
        try:
            success = True
            # Use getattr to avoid repeating; assumes setting_key matches config property name
            sections = {'General': ['log_level', 'log_file'],
                        'Repository': ['type', 'workflows_path', 'credentials_path', 'db_path', 'create_if_missing'],
                        'WebDriver': ['default_browser', 'implicit_wait', 'chrome_driver_path', 'firefox_driver_path', 'edge_driver_path']}

            for section, keys in sections.items():
                for key in keys:
                    # Map UI key to config property if names differ, here they match
                    config_key = key
                    # Handle boolean conversion for saving
                    value_to_save = settings_to_save.get(config_key)
                    if isinstance(value_to_save, bool):
                         value_str = str(value_to_save).lower()
                    else:
                         value_str = str(value_to_save)

                    success &= self.config.save_setting(section, config_key, value_str)

            if not success:
                 # Should not happen if save_setting handles errors well, but check
                 raise ConfigError("Failed to update one or more settings in memory.")

            # --- Write changes to file ---
            if self.config.save_config_to_file(): # This can raise IO/Config errors
                self.logger.info("Settings saved to config.ini.")
                self.view.set_status("Settings saved successfully.")
                # Reload config internally and update view to reflect saved state
                self.load_settings()
            else:
                 # save_config_to_file failed (should raise error caught by decorator)
                 raise ConfigError("Failed to write settings to config.ini file.")

        except Exception as e:
             # Let the decorator handle logging/displaying unexpected errors during save
             raise ConfigError(f"An unexpected error occurred during save: {e}", cause=e) from e


    # No decorator needed for simple reload trigger
    def cancel_changes(self) -> None:
        """Discard changes and reload settings from the file."""
        self.logger.info("Cancelling settings changes, reloading from file.")
        self.load_settings() # Reload settings from file, decorator handles errors

########## END FILE: src/ui/presenters/settings_presenter.py ##########


########## START FILE: src/infrastructure/repositories/database_workflow_repository.py ##########
# GROUP: Group 3: COULD ADD

"""Database workflow repository implementation for AutoQliq."""
import json
import logging
import sqlite3 # Import sqlite3 for specific DB errors if needed
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core dependencies
from src.core.interfaces import IAction, IWorkflowRepository
from src.core.exceptions import WorkflowError, RepositoryError, SerializationError, ValidationError

# Infrastructure dependencies
from src.infrastructure.common.error_handling import handle_exceptions
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.common.validators import WorkflowValidator
from src.infrastructure.repositories.base.database_repository import DatabaseRepository
from src.infrastructure.repositories.serialization.action_serializer import (
    serialize_actions,
    deserialize_actions
)

logger = logging.getLogger(__name__)

class DatabaseWorkflowRepository(DatabaseRepository[List[IAction]], IWorkflowRepository):
    """
    Implementation of IWorkflowRepository storing workflows and templates in SQLite.
    """
    _WF_TABLE_NAME = "workflows"
    _WF_PK_COLUMN = "name"
    _TMPL_TABLE_NAME = "templates"
    _TMPL_PK_COLUMN = "name"

    def __init__(self, db_path: str, **options: Any):
        """Initialize DatabaseWorkflowRepository."""
        super().__init__(db_path=db_path, table_name=self._WF_TABLE_NAME, logger_name=__name__)
        self._create_templates_table_if_not_exists()

    # --- Configuration for Workflows Table (via Base Class) ---
    def _get_primary_key_col(self) -> str: return self._WF_PK_COLUMN
    def _get_table_creation_sql(self) -> str:
        return f"{self._WF_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL"

    # --- Configuration and Creation for Templates Table ---
    def _get_templates_table_creation_sql(self) -> str:
         """Return SQL for creating the templates table."""
         # Added modified_at for templates as well
         return f"{self._TMPL_PK_COLUMN} TEXT PRIMARY KEY NOT NULL, actions_json TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL"

    def _create_templates_table_if_not_exists(self) -> None:
        """Create the templates table."""
        logger.debug("Ensuring templates table exists.")
        sql = self._get_templates_table_creation_sql()
        try: self.connection_manager.create_table(self._TMPL_TABLE_NAME, sql)
        except Exception as e: logger.error(f"Failed ensure table '{self._TMPL_TABLE_NAME}': {e}", exc_info=True)


    # --- Mapping for Workflows (Base Class uses these) ---
    def _map_row_to_entity(self, row: Dict[str, Any]) -> List[IAction]:
        """Convert a workflow table row to a list of IAction."""
        actions_json = row.get("actions_json"); name = row.get(self._WF_PK_COLUMN, "<unknown>")
        if actions_json is None: raise RepositoryError(f"Missing action data for workflow '{name}'.", entity_id=name)
        try:
            action_data_list = json.loads(actions_json)
            if not isinstance(action_data_list, list): raise json.JSONDecodeError("Not JSON list.", actions_json, 0)
            return deserialize_actions(action_data_list) # Raises SerializationError
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in workflow '{name}': {e}", entity_id=name, cause=e) from e
        except Exception as e:
             if isinstance(e, SerializationError): raise
             raise RepositoryError(f"Error processing actions for workflow '{name}': {e}", entity_id=name, cause=e) from e

    def _map_entity_to_params(self, entity_id: str, entity: List[IAction]) -> Dict[str, Any]:
        """Convert list of IAction to workflow DB parameters."""
        WorkflowValidator.validate_workflow_name(entity_id)
        WorkflowValidator.validate_actions(entity)
        try:
            action_data_list = serialize_actions(entity) # Raises SerializationError
            actions_json = json.dumps(action_data_list)
        except (SerializationError, TypeError) as e: raise SerializationError(f"Failed serialize actions for workflow '{entity_id}'", entity_id=entity_id, cause=e) from e
        now = datetime.now().isoformat()
        return { self._WF_PK_COLUMN: entity_id, "actions_json": actions_json, "created_at": now, "modified_at": now }

    # --- IWorkflowRepository Implementation (using Base Class methods) ---
    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error saving workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def save(self, name: str, workflow_actions: List[IAction]) -> None: super().save(name, workflow_actions)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error loading workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError, SerializationError))
    def load(self, name: str) -> List[IAction]:
        actions = super().get(name)
        if actions is None: raise RepositoryError(f"Workflow not found: '{name}'", entity_id=name)
        return actions

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error deleting workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def delete(self, name: str) -> bool: return super().delete(name)

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error listing workflows", reraise_types=(RepositoryError,))
    def list_workflows(self) -> List[str]: return super().list()

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error getting workflow metadata", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def get_metadata(self, name: str) -> Dict[str, Any]:
        self._validate_entity_id(name, entity_type="Workflow")
        self._log_operation("Getting metadata", name)
        try:
            query = f"SELECT {self._WF_PK_COLUMN}, created_at, modified_at FROM {self._WF_TABLE_NAME} WHERE {self._WF_PK_COLUMN} = ?"
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Workflow not found: {name}", entity_id=name)
            metadata = dict(rows[0]); metadata["source"] = "database"
            return metadata
        except RepositoryError: raise
        except Exception as e: raise RepositoryError(f"Failed get metadata for workflow '{name}'", entity_id=name, cause=e) from e

    @log_method_call(logger)
    @handle_exceptions(WorkflowError, "Error creating empty workflow", reraise_types=(WorkflowError, ValidationError, RepositoryError))
    def create_workflow(self, name: str) -> None:
        WorkflowValidator.validate_workflow_name(name)
        self._log_operation("Creating empty workflow", name)
        if super().get(name) is not None: raise RepositoryError(f"Workflow '{name}' already exists.", entity_id=name)
        try: super().save(name, []) # Save empty list
        except Exception as e: raise WorkflowError(f"Failed create empty workflow '{name}'", workflow_name=name, cause=e) from e

    # --- Template Methods (DB Implementation) ---

    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error saving template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def save_template(self, name: str, actions_data: List[Dict[str, Any]]) -> None:
        """Save/Update an action template (serialized list) to the DB."""
        self._validate_entity_id(name, entity_type="Template") # Use base validator
        self._log_operation("Saving template", name)
        if not isinstance(actions_data, list) or not all(isinstance(item, dict) for item in actions_data):
             raise SerializationError("Template actions data must be list of dicts.")
        try: actions_json = json.dumps(actions_data)
        except TypeError as e: raise SerializationError(f"Data for template '{name}' not JSON serializable", entity_id=name, cause=e) from e

        now = datetime.now().isoformat()
        pk_col = self._TMPL_PK_COLUMN
        # Include modified_at for templates table as well
        params = {pk_col: name, "actions_json": actions_json, "created_at": now, "modified_at": now}
        columns = list(params.keys()); placeholders = ", ".join("?" * len(params))
        # Update actions_json and modified_at on conflict
        update_cols = ["actions_json", "modified_at"]
        updates = ", ".join(f"{col} = ?" for col in update_cols)
        query = f"""
            INSERT INTO {self._TMPL_TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders})
            ON CONFLICT({pk_col}) DO UPDATE SET {updates}
        """
        # Values: name, json, created, modified, json_update, modified_update
        final_params = (name, actions_json, now, now, actions_json, now)
        try:
            self.connection_manager.execute_modification(query, final_params)
            self.logger.info(f"Successfully saved template: '{name}'")
        except Exception as e: raise RepositoryError(f"DB error saving template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error loading template", reraise_types=(ValidationError, RepositoryError, SerializationError))
    def load_template(self, name: str) -> List[Dict[str, Any]]:
        """Load serialized action data for a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Loading template", name)
        query = f"SELECT actions_json FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            rows = self.connection_manager.execute_query(query, (name,))
            if not rows: raise RepositoryError(f"Template not found: {name}", entity_id=name)
            actions_json = rows[0]["actions_json"]
            actions_data = json.loads(actions_json) # Raises JSONDecodeError
            if not isinstance(actions_data, list): raise SerializationError(f"Stored template '{name}' not JSON list.", entity_id=name)
            if not all(isinstance(item, dict) for item in actions_data): raise SerializationError(f"Stored template '{name}' contains non-dict items.", entity_id=name)
            return actions_data
        except RepositoryError: raise
        except json.JSONDecodeError as e: raise SerializationError(f"Invalid JSON in template '{name}'", entity_id=name, cause=e) from e
        except Exception as e: raise RepositoryError(f"DB error loading template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error deleting template", reraise_types=(ValidationError, RepositoryError))
    def delete_template(self, name: str) -> bool:
        """Delete a template from the DB."""
        self._validate_entity_id(name, entity_type="Template")
        self._log_operation("Deleting template", name)
        query = f"DELETE FROM {self._TMPL_TABLE_NAME} WHERE {self._TMPL_PK_COLUMN} = ?"
        try:
            affected_rows = self.connection_manager.execute_modification(query, (name,))
            deleted = affected_rows > 0
            if deleted: self.logger.info(f"Successfully deleted template: '{name}'")
            else: self.logger.warning(f"Template not found for deletion: '{name}'")
            return deleted
        except Exception as e: raise RepositoryError(f"DB error deleting template '{name}'", entity_id=name, cause=e) from e


    @log_method_call(logger)
    @handle_exceptions(RepositoryError, "Error listing templates")
    def list_templates(self) -> List[str]:
        """List the names of all saved templates."""
        self._log_operation("Listing templates")
        query = f"SELECT {self._TMPL_PK_COLUMN} FROM {self._TMPL_TABLE_NAME} ORDER BY {self._TMPL_PK_COLUMN}"
        try:
            rows = self.connection_manager.execute_query(query)
            names = [row[self._TMPL_PK_COLUMN] for row in rows]
            return names
        except Exception as e: raise RepositoryError(f"DB error listing templates", cause=e) from e

########## END FILE: src/infrastructure/repositories/database_workflow_repository.py ##########


########## START FILE: src/infrastructure/webdrivers/selenium_driver.py ##########
# GROUP: Group 3: COULD ADD

"""Selenium WebDriver implementation for AutoQliq."""
import logging
import os
from typing import Any, Optional, Union

# Selenium imports
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, JavascriptException

# Core imports
from src.core.interfaces import IWebDriver
from src.core.exceptions import WebDriverError, ConfigError, ValidationError

# Infrastructure imports
from src.infrastructure.common.logging_utils import log_method_call
from src.infrastructure.webdrivers.error_handler import handle_driver_exceptions, map_webdriver_exception
from src.infrastructure.webdrivers.base import BrowserType

# Import Selenium options classes
from selenium.webdriver import ChromeOptions, FirefoxOptions, EdgeOptions, SafariOptions

logger = logging.getLogger(__name__)


class SeleniumWebDriver(IWebDriver):
    """
    Implementation of IWebDriver using Selenium WebDriver.
    Handles driver initialization and wraps Selenium methods.
    """
    _DEFAULT_WAIT_TIMEOUT = 10 # Default explicit wait timeout in seconds

    def __init__(self,
                 browser_type: BrowserType = BrowserType.CHROME,
                 implicit_wait_seconds: int = 0,
                 selenium_options: Optional[Any] = None,
                 webdriver_path: Optional[str] = None):
        """Initialize SeleniumWebDriver and the underlying Selenium driver."""
        self.browser_type = browser_type
        self.implicit_wait_seconds = implicit_wait_seconds
        self.driver: Optional[RemoteWebDriver] = None
        logger.info(f"Initializing SeleniumWebDriver for: {self.browser_type.value}")

        try:
            options_instance = self._resolve_options(selenium_options)
            service_instance = self._create_service(webdriver_path)

            logger.info(f"Attempting to create Selenium WebDriver instance...")
            driver_map = { BrowserType.CHROME: webdriver.Chrome, BrowserType.FIREFOX: webdriver.Firefox,
                           BrowserType.EDGE: webdriver.Edge, BrowserType.SAFARI: webdriver.Safari }
            driver_class = driver_map.get(browser_type)
            if driver_class is None: raise ConfigError(f"Unsupported browser: {browser_type}")

            if browser_type == BrowserType.SAFARI:
                 if service_instance: logger.warning("webdriver_path ignored for Safari.")
                 self.driver = driver_class(options=options_instance)
            else:
                 self.driver = driver_class(service=service_instance, options=options_instance)

            logger.info(f"Successfully created Selenium {browser_type.value} WebDriver instance.")
            if self.implicit_wait_seconds > 0:
                self.driver.implicitly_wait(self.implicit_wait_seconds)
                logger.debug(f"Set implicit wait to {self.implicit_wait_seconds} seconds")

        except WebDriverException as e:
             err_msg = f"Failed initialize Selenium {browser_type.value}: {e.msg}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e
        except Exception as e:
             err_msg = f"Unexpected error initializing SeleniumWebDriver: {e}"
             logger.error(err_msg, exc_info=True)
             raise WebDriverError(err_msg, driver_type=self.browser_type.value, cause=e) from e

    def _resolve_options(self, options_param: Optional[Any]) -> Optional[Any]:
        """Returns the appropriate options object or None."""
        if options_param:
             expected_type = { BrowserType.CHROME: ChromeOptions, BrowserType.FIREFOX: FirefoxOptions,
                               BrowserType.EDGE: EdgeOptions, BrowserType.SAFARI: SafariOptions }.get(self.browser_type)
             if expected_type and not isinstance(options_param, expected_type):
                  logger.warning(f"Provided options type ({type(options_param).__name__}) might not match browser ({self.browser_type.value}).")
             return options_param
        else:
             logger.debug(f"No specific Selenium options provided for {self.browser_type.value}. Using defaults.")
             if self.browser_type == BrowserType.CHROME: return ChromeOptions()
             if self.browser_type == BrowserType.FIREFOX: return FirefoxOptions()
             if self.browser_type == BrowserType.EDGE: return EdgeOptions()
             if self.browser_type == BrowserType.SAFARI: return SafariOptions()
             return None

    def _create_service(self, webdriver_path: Optional[str]) -> Optional[Any]:
         """Creates a Selenium Service object if a path is provided."""
         from selenium.webdriver.chrome.service import Service as ChromeService
         from selenium.webdriver.firefox.service import Service as FirefoxService
         from selenium.webdriver.edge.service import Service as EdgeService
         service_map = { BrowserType.CHROME: ChromeService, BrowserType.FIREFOX: FirefoxService, BrowserType.EDGE: EdgeService }
         service_class = service_map.get(self.browser_type)
         if service_class and webdriver_path:
              if not os.path.exists(webdriver_path): raise ConfigError(f"WebDriver executable not found: {webdriver_path}")
              logger.info(f"Using explicit webdriver path: {webdriver_path}")
              return service_class(executable_path=webdriver_path)
         elif webdriver_path: logger.warning(f"webdriver_path '{webdriver_path}' ignored for {self.browser_type.value}.")
         else: logger.debug(f"Using Selenium Manager or system PATH for {self.browser_type.value}.")
         return None

    def _ensure_driver(self) -> RemoteWebDriver:
        """Checks if the driver is initialized."""
        if self.driver is None: raise WebDriverError("WebDriver not initialized or has been quit.")
        return self.driver

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to navigate to URL: {url}")
    def get(self, url: str) -> None:
        if not isinstance(url, str) or not url: raise ValidationError("URL must be non-empty string.", field_name="url")
        driver = self._ensure_driver(); driver.get(url)

    @log_method_call(logger, log_result=False)
    def quit(self) -> None:
        driver = self.driver
        if driver:
            try: driver.quit(); logger.info(f"Selenium WebDriver ({self.browser_type.value}) quit.")
            except Exception as e: logger.error(f"Error quitting Selenium WebDriver: {e}", exc_info=False)
            finally: self.driver = None

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to find element with selector: {selector}")
    def find_element(self, selector: str) -> WebElement:
        if not isinstance(selector, str) or not selector: raise ValidationError("Selector must be non-empty string.", field_name="selector")
        driver = self._ensure_driver()
        try: return driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException as e: raise WebDriverError(f"Element not found for selector: {selector}", cause=e) from e

    @log_method_call(logger, log_args=True)
    @handle_driver_exceptions("Failed to click element with selector: {selector}")
    def click_element(self, selector: str) -> None:
        element = self.find_element(selector); element.click()

    @log_method_call(logger, log_args=False)
    @handle_driver_exceptions("Failed to type text into element with selector: {selector}")
    def type_text(self, selector: str, text: str) -> None:
        if not isinstance(text, str): raise ValidationError("Text must be string.", field_name="text")
        element = self.find_element(selector); element.clear(); element.send_keys(text)
        logger.debug(f"Typed text (length {len(text)}) into element: {selector}")

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to take screenshot to file: {file_path}")
    def take_screenshot(self, file_path: str) -> None:
        if not isinstance(file_path, str) or not file_path: raise ValidationError("File path must be non-empty string.", field_name="file_path")
        driver = self._ensure_driver()
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory): os.makedirs(directory, exist_ok=True)
            if not driver.save_screenshot(file_path): raise WebDriverError(f"WebDriver failed saving screenshot to {file_path}")
        except (IOError, OSError) as e: raise WebDriverError(f"File system error saving screenshot to {file_path}: {e}") from e

    def is_element_present(self, selector: str) -> bool:
        if not isinstance(selector, str) or not selector: logger.warning("is_element_present empty selector."); return False
        driver = self._ensure_driver(); original_wait = self.implicit_wait_seconds; present = False
        try:
             if original_wait > 0: driver.implicitly_wait(0)
             elements = driver.find_elements(By.CSS_SELECTOR, selector); present = len(elements) > 0
        except WebDriverException as e: logger.error(f"Error checking presence of '{selector}': {e}"); present = False
        finally:
             if original_wait > 0:
                  try: driver.implicitly_wait(original_wait)
                  except Exception: logger.warning("Could not restore implicit wait.")
        return present

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get current URL")
    def get_current_url(self) -> str:
        driver = self._ensure_driver(); return driver.current_url

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to execute script")
    def execute_script(self, script: str, *args: Any) -> Any:
        """Executes JavaScript."""
        if not isinstance(script, str): raise ValidationError("Script must be a string.", field_name="script")
        driver = self._ensure_driver()
        try: return driver.execute_script(script, *args)
        except JavascriptException as e: raise WebDriverError(f"JavaScript execution error: {e.msg}", cause=e) from e

    @log_method_call(logger)
    @handle_driver_exceptions("Failed waiting for element with selector: {selector}")
    def wait_for_element(self, selector: str, timeout: int = _DEFAULT_WAIT_TIMEOUT) -> WebElement:
        """Wait explicitly for an element to be present."""
        if not isinstance(selector, str) or not selector: raise ValidationError("Selector must be non-empty string.", field_name="selector")
        if not isinstance(timeout, (int, float)) or timeout <= 0: timeout = self._DEFAULT_WAIT_TIMEOUT
        driver = self._ensure_driver(); wait = WebDriverWait(driver, timeout)
        try: return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException as e: raise WebDriverError(f"Timeout waiting for element: {selector}", cause=e) from e

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to frame: {frame_reference}")
    def switch_to_frame(self, frame_reference: Union[str, int, WebElement]) -> None:
        driver = self._ensure_driver(); driver.switch_to.frame(frame_reference)

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to switch to default content")
    def switch_to_default_content(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.default_content()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to accept alert")
    def accept_alert(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.alert.accept()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to dismiss alert")
    def dismiss_alert(self) -> None:
        driver = self._ensure_driver(); driver.switch_to.alert.dismiss()

    @log_method_call(logger)
    @handle_driver_exceptions("Failed to get alert text")
    def get_alert_text(self) -> str:
        driver = self._ensure_driver(); return driver.switch_to.alert.text

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.quit()

########## END FILE: src/infrastructure/webdrivers/selenium_driver.py ##########


########## START FILE: src/core/actions/navigation.py ##########
# GROUP: Group 3: COULD ADD

"""Navigation actions module for AutoQliq."""

import logging
from typing import Dict, Any, Optional
import re

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, ValidationError

logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

class NavigateAction(ActionBase):
    """Action to navigate the browser to a specified URL."""
    action_type: str = "Navigate"

    def __init__(self, url: str, name: Optional[str] = None, **kwargs):
        """Initialize a NavigateAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(url, str) or not url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(url):
             logger.warning(f"URL '{url}' may not be valid for NavigateAction '{self.name}'.")
        self.url = url
        logger.debug(f"NavigateAction '{self.name}' initialized for URL: '{self.url}'")

    def validate(self) -> bool:
        """Validate the URL."""
        super().validate()
        if not isinstance(self.url, str) or not self.url:
            raise ValidationError("URL must be a non-empty string.", field_name="url")
        if not URL_PATTERN.match(self.url):
             logger.warning(f"URL '{self.url}' may not be valid during validation.")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the navigation action."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) to URL: '{self.url}'")
        try:
            self.validate()
            driver.get(self.url) # Raises WebDriverError on failure
            msg = f"Successfully navigated to URL: {self.url}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            msg = f"Error navigating to '{self.url}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error navigating to '{self.url}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action."""
        base_dict = super().to_dict()
        base_dict["url"] = self.url
        return base_dict

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(name='{self.name}', url='{self.url}')"

########## END FILE: src/core/actions/navigation.py ##########


########## START FILE: src/core/actions/interaction.py ##########
# GROUP: Group 3: COULD ADD

"""Interaction actions module for AutoQliq.

Contains actions that simulate user interactions with web elements,
such as clicking or typing.
"""

import logging
from typing import Dict, Any, Optional

from src.core.actions.base import ActionBase
from src.core.action_result import ActionResult
from src.core.interfaces import IWebDriver, ICredentialRepository
from src.core.exceptions import WebDriverError, ActionError, CredentialError, ValidationError

logger = logging.getLogger(__name__)


class ClickAction(ActionBase):
    """
    Action to click on a web element identified by a CSS selector.
    """
    action_type: str = "Click"

    def __init__(self, selector: str, name: Optional[str] = None, **kwargs):
        """Initialize a ClickAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        self.selector = selector
        logger.debug(f"ClickAction '{self.name}' initialized for selector: '{self.selector}'")

    def validate(self) -> bool:
        """Validate that the selector is a non-empty string."""
        super().validate()
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        return True

    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the click action using the web driver."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate()
            driver.click_element(self.selector) # Raises WebDriverError on failure
            msg = f"Successfully clicked element with selector: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, WebDriverError) as e:
            msg = f"Error clicking element '{self.selector}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error clicking element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["selector"] = self.selector
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}')"


class TypeAction(ActionBase):
    """
    Action to type text into a web element identified by a CSS selector.
    Uses `value_type` ('text' or 'credential') and `value_key` (the literal
    text or the credential key like 'login.username') to determine the source
    of the text.
    """
    action_type: str = "Type"

    def __init__(self, selector: str, value_key: str, value_type: str, name: Optional[str] = None, **kwargs):
        """Initialize a TypeAction."""
        super().__init__(name or self.action_type, **kwargs)
        if not isinstance(selector, str) or not selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(value_key, str): # Allow empty string for text value
             raise ValidationError("Value key must be a string.", field_name="value_key")
        if value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")
        if value_type == "credential" and not value_key:
             raise ValidationError("Credential key cannot be empty when value_type is 'credential'.", field_name="value_key")

        self.selector = selector
        self.value_key = value_key
        self.value_type = value_type
        logger.debug(f"TypeAction '{self.name}' initialized for selector: '{self.selector}', type: {self.value_type}")

    def validate(self) -> bool:
        """Validate that selector, value_key, and value_type are set correctly."""
        super().validate()
        if not isinstance(self.selector, str) or not self.selector:
            raise ValidationError("Selector must be a non-empty string.", field_name="selector")
        if not isinstance(self.value_key, str):
             raise ValidationError("Value key must be a string.", field_name="value_key")
        if self.value_type not in ["text", "credential"]:
             raise ValidationError("value_type must be either 'text' or 'credential'.", field_name="value_type")
        if self.value_type == "credential":
            if not self.value_key:
                raise ValidationError("Credential key cannot be empty.", field_name="value_key")
            if '.' not in self.value_key:
                raise ValidationError("Credential key format should be 'credential_name.field'.", field_name="value_key")
        return True

    def _resolve_text(self, credential_repo: Optional[ICredentialRepository]) -> str:
        """Resolve the text to be typed."""
        if self.value_type == "text":
            return self.value_key
        elif self.value_type == "credential":
            if credential_repo is None:
                raise CredentialError(f"Credential repo needed for action '{self.name}'.")

            key_parts = self.value_key.split('.', 1)
            if len(key_parts) != 2: raise ValidationError(f"Invalid credential key format '{self.value_key}'.", field_name="value_key")
            credential_name, field_key = key_parts
            if not credential_name or not field_key: raise ValidationError(f"Invalid credential key format '{self.value_key}'.", field_name="value_key")

            try:
                credential_dict = credential_repo.get_by_name(credential_name) # Raises ValidationError on bad name format
                if credential_dict is None: raise CredentialError(f"Credential '{credential_name}' not found.", credential_name=credential_name)
                if field_key not in credential_dict: raise CredentialError(f"Field '{field_key}' not found in credential '{credential_name}'.", credential_name=credential_name)
                resolved_value = credential_dict[field_key]
                logger.debug(f"Resolved credential field '{field_key}' for '{credential_name}'.")
                return str(resolved_value) if resolved_value is not None else ""
            except ValidationError as e: raise CredentialError(f"Invalid credential name format '{credential_name}': {e}", credential_name=credential_name, cause=e) from e
            except CredentialError: raise
            except Exception as e: raise CredentialError(f"Failed to retrieve credential '{credential_name}': {e}", credential_name=credential_name, cause=e) from e
        else:
             raise ActionError(f"Unsupported value_type '{self.value_type}' in action '{self.name}'.")


    def execute(
        self,
        driver: IWebDriver,
        credential_repo: Optional[ICredentialRepository] = None,
        context: Optional[Dict[str, Any]] = None # Accept context
    ) -> ActionResult:
        """Execute the type action using the web driver."""
        logger.info(f"Executing {self.action_type} action (Name: {self.name}) on selector: '{self.selector}'")
        try:
            self.validate()
            # Pass the specific credential repo instance needed for resolution
            text_to_type = self._resolve_text(credential_repo) # Raises CredentialError/ValidationError
            logger.debug(f"Typing text (length {len(text_to_type)}) into '{self.selector}'")
            driver.type_text(self.selector, text_to_type) # Raises WebDriverError
            msg = f"Successfully typed text into element: {self.selector}"
            logger.debug(msg)
            return ActionResult.success(msg)
        except (ValidationError, CredentialError, WebDriverError) as e:
            msg = f"Error typing into element '{self.selector}': {e}"
            logger.error(msg)
            return ActionResult.failure(msg)
        except Exception as e:
            error = ActionError(f"Unexpected error typing into element '{self.selector}'", action_name=self.name, action_type=self.action_type, cause=e)
            logger.error(str(error), exc_info=True)
            return ActionResult.failure(str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the action to a dictionary."""
        base_dict = super().to_dict()
        base_dict["selector"] = self.selector
        base_dict["value_key"] = self.value_key
        base_dict["value_type"] = self.value_type
        return base_dict

    def __repr__(self) -> str:
        """Return a developer-friendly string representation."""
        value_repr = f"text:'{self.value_key}'" if self.value_type == 'text' else f"credential:'{self.value_key}'"
        return f"{self.__class__.__name__}(name='{self.name}', selector='{self.selector}', {value_repr})"

########## END FILE: src/core/actions/interaction.py ##########


########## START FILE: tests/unit/core/test_workflow.py ##########
# GROUP: Group 3: COULD ADD

"""Unit tests for the WorkflowRunner."""

import unittest
from unittest.mock import MagicMock, call, ANY, patch
import threading # For stop event

# Assuming correct paths for imports
from src.core.workflow.runner import WorkflowRunner
from src.core.interfaces import IWebDriver, ICredentialRepository, IWorkflowRepository, IAction
from src.core.action_result import ActionResult, ActionStatus
from src.core.exceptions import WorkflowError, ActionError, RepositoryError, ValidationError, SerializationError
# Import action types used in tests
from src.core.actions.base import ActionBase
from src.core.actions.conditional_action import ConditionalAction
from src.core.actions.loop_action import LoopAction
from src.core.actions.error_handling_action import ErrorHandlingAction
from src.core.actions.template_action import TemplateAction
# Mock ActionFactory for template tests
# from src.core.actions.factory import ActionFactory # Not needed directly if mocking expander

# --- Mock Actions ---
class MockWFAction(ActionBase):
    action_type = "MockWF"
    def __init__(self, name="MockWFAction", succeed=True, msg="", raise_exc=None, delay=0):
        super().__init__(name); self.succeed = succeed; self.msg = msg; self.raise_exc = raise_exc; self.delay = delay
        self.execute = MagicMock(side_effect=self._mock_execute) # type: ignore
        self.validate = MagicMock(return_value=True)
    def _mock_execute(self, driver, credential_repo=None, context=None):
         if self.delay > 0: time.sleep(self.delay)
         stop_event = context.get('_stop_event_runner') if context else None # Check internal flag if needed
         if stop_event and stop_event.is_set(): raise WorkflowError("Stopped during action execute")
         if self.raise_exc: raise self.raise_exc
         if self.succeed: return ActionResult.success(self.msg or f"{self.name} OK")
         else: return ActionResult.failure(self.msg or f"{self.name} FAILED")
    def to_dict(self): return {"type":self.action_type, "name":self.name}

# --- Test Suite ---
class TestWorkflowRunner(unittest.TestCase):
    """Test suite for WorkflowRunner."""

    def setUp(self):
        """Set up mocks for each test."""
        self.mock_driver = MagicMock(spec=IWebDriver)
        self.mock_cred_repo = MagicMock(spec=ICredentialRepository)
        self.mock_wf_repo = MagicMock(spec=IWorkflowRepository)
        self.mock_stop_event = MagicMock(spec=threading.Event)
        self.mock_stop_event.is_set.return_value = False

        self.runner = WorkflowRunner(self.mock_driver, self.mock_cred_repo, self.mock_wf_repo, self.mock_stop_event)
        # Patch _execute_actions to track calls to it if needed for complex flow tests
        self.exec_actions_patcher = patch.object(self.runner, '_execute_actions', wraps=self.runner._execute_actions)
        self.mock_execute_actions = self.exec_actions_patcher.start()
        # Patch _expand_template for tests not focusing on it
        self.expand_template_patcher = patch.object(self.runner, '_expand_template', wraps=self.runner._expand_template)
        self.mock_expand_template = self.expand_template_patcher.start()


    def tearDown(self):
        self.exec_actions_patcher.stop()
        self.expand_template_patcher.stop()

    # --- Basic Execution Tests ---
    def test_run_success_returns_log_dict(self):
        """Test successful run returns a detailed log dictionary."""
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2")
        actions = [action1, action2]; start_time = time.time()
        log_data = self.runner.run(actions, "SuccessWF")
        end_time = time.time()
        self.assertEqual(log_data['final_status'], "SUCCESS"); self.assertIsNone(log_data['error_message'])
        self.assertEqual(len(log_data['action_results']), 2)
        self.assertEqual(log_data['action_results'][0], {"status": "success", "message": "Action1 OK"})
        action1.execute.assert_called_once_with(self.mock_driver, self.mock_cred_repo, ANY)
        action2.execute.assert_called_once_with(self.mock_driver, self.mock_cred_repo, ANY)
        self.assertEqual(action1.execute.call_args[0][2], {}) # Check context
        self.assertEqual(action2.execute.call_args[0][2], {})

    def test_run_failure_returns_log_dict_and_raises(self):
        """Test failing run raises WorkflowError but returns log dict in finally block (if applicable)."""
        # Note: The current runner `run` method raises on failure, it doesn't return the log dict in that case.
        # The caller (WorkflowService) catches the exception and builds the final log.
        # This test verifies the exception is raised correctly.
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2", succeed=False, msg="It failed")
        actions = [action1, action2]
        with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "FailureWF")
        self.assertIsInstance(cm.exception.__cause__, ActionError); self.assertIn("It failed", str(cm.exception.__cause__))
        action1.execute.assert_called_once(); action2.execute.assert_called_once()

    def test_run_exception_returns_log_dict_and_raises(self):
        """Test run with exception raises WorkflowError."""
        action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2", raise_exc=ValueError("Action broke"))
        actions = [action1, action2]
        with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "ExceptionWF")
        self.assertIsInstance(cm.exception.__cause__, ActionError) # run_single_action wraps it
        self.assertIsInstance(cm.exception.__cause__.__cause__, ValueError)
        action1.execute.assert_called_once(); action2.execute.assert_called_once()

    # --- Context and Control Flow Tests ---
    def test_run_loop_passes_context(self):
         """Test context (loop vars) is passed correctly during loop execution."""
         inner_action = MockWFAction("Inner")
         loop_action = LoopAction(name="Loop3", count=2, loop_actions=[inner_action])
         # Mock LoopAction's execute to check context passed to _execute_actions
         loop_action.execute = MagicMock(wraps=loop_action.execute)

         self.runner.run([loop_action], "LoopContextWF")

         # Check _execute_actions was called inside the loop's execute
         # Need to inspect calls made *by* the real LoopAction.execute
         # This requires patching _execute_actions on the *runner instance* used inside LoopAction.
         # Simpler: Check the context received by the inner action's mock.
         self.assertEqual(inner_action.execute.call_count, 2)
         ctx1 = inner_action.execute.call_args_list[0][0][2]; self.assertEqual(ctx1, {'loop_index': 0, 'loop_iteration': 1, 'loop_total': 2})
         ctx2 = inner_action.execute.call_args_list[1][0][2]; self.assertEqual(ctx2, {'loop_index': 1, 'loop_iteration': 2, 'loop_total': 2})

    # --- Template Expansion Tests ---
    @patch('src.core.workflow.runner.ActionFactory', MagicMock()) # Mock factory within runner module
    def test_run_template_expansion(self, MockActionFactory):
         """Test runner expands TemplateAction using WorkflowRepository."""
         action1 = MockWFAction("Action1"); template_name = "my_tmpl"
         template_action = TemplateAction(name="UseTemplate", template_name=template_name)
         action3 = MockWFAction("Action3"); workflow_actions = [action1, template_action, action3]
         t_action1 = MockWFAction("TmplAct1"); t_action2 = MockWFAction("TmplAct2")
         template_data = [{"type":"MockWF", "name":"TmplAct1"}, {"type":"MockWF", "name":"TmplAct2"}]
         template_actions_objs = [t_action1, t_action2]
         self.mock_wf_repo.load_template.return_value = template_data
         MockActionFactory.create_action.side_effect = lambda data: MockWFAction(name=data['name'])

         log_data = self.runner.run(workflow_actions, "TemplateWF")

         self.mock_wf_repo.load_template.assert_called_once_with(template_name)
         MockActionFactory.create_action.assert_has_calls([call(template_data[0]), call(template_data[1])])
         # Verify execution order via mocks on action instances
         action1.execute.assert_called_once()
         t_action1.execute.assert_called_once()
         t_action2.execute.assert_called_once()
         action3.execute.assert_called_once()
         self.assertEqual(log_data['final_status'], "SUCCESS"); self.assertEqual(len(log_data['action_results']), 4)

    def test_run_template_load_fails(self):
         """Test runner fails workflow if template load fails."""
         template_name = "bad_tmpl"; action1 = MockWFAction("Action1")
         template_action = TemplateAction(name="UseBadTemplate", template_name=template_name)
         actions = [action1, template_action]
         repo_error = RepositoryError("Template not found"); self.mock_wf_repo.load_template.side_effect = repo_error

         with self.assertRaises(WorkflowError) as cm: self.runner.run(actions, "TemplateFailWF")
         self.assertIsInstance(cm.exception.__cause__, ActionError); self.assertIn("Template expansion failed", str(cm.exception.__cause__))
         self.assertIsInstance(cm.exception.__cause__.__cause__, RepositoryError)
         action1.execute.assert_called_once() # Action 1 ran

    # --- Stop Event Tests ---
    def test_run_checks_stop_event(self):
         """Test runner checks stop event before each action."""
         action1 = MockWFAction("Action1"); action2 = MockWFAction("Action2"); actions = [action1, action2]
         call_count = 0
         def stop_side_effect(): nonlocal call_count; call_count += 1; return call_count > 1
         self.mock_stop_event.is_set.side_effect = stop_side_effect

         with self.assertRaisesRegex(WorkflowError, "Stop requested"): self.runner.run(actions, "StopWF")
         self.assertEqual(self.mock_stop_event.is_set.call_count, 2); action1.execute.assert_called_once(); action2.execute.assert_not_called()

# Need time and timedelta for log dict checks
import time
from datetime import datetime, timedelta

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

########## END FILE: tests/unit/core/test_workflow.py ##########


########## START FILE: tests/unit/application/test_credential_service.py ##########
# GROUP: Group 3: COULD ADD

"""Unit tests for the CredentialService."""

import unittest
from unittest.mock import MagicMock, patch, call, ANY

# Assuming correct paths for imports
from src.application.services.credential_service import CredentialService, WERKZEUG_AVAILABLE
from src.core.interfaces import ICredentialRepository
from src.core.exceptions import CredentialError, ValidationError, RepositoryError

# Mock werkzeug hashing functions if available, otherwise use simple mocks
MOCK_HASH_PREFIX = "hashed$" if WERKZEUG_AVAILABLE else "plaintext:"
def mock_generate_hash(password, method, salt_length):
    # Simulate prefix based on availability for realistic testing
    prefix = "pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:"
    return prefix + password # Simple mock, not real hashing

def mock_check_hash(pwhash, password):
    if pwhash is None: return False
    if pwhash.startswith("pbkdf2:"):
         # Simulate check for mock hash
         return pwhash[len("pbkdf2:"):] == password
    elif pwhash.startswith("plaintext:"):
        # Simulate check for plaintext fallback
        return pwhash[len("plaintext:"):] == password
    return False # Unknown hash format


@patch('src.application.services.credential_service.generate_password_hash', side_effect=mock_generate_hash)
@patch('src.application.services.credential_service.check_password_hash', side_effect=mock_check_hash)
class TestCredentialService(unittest.TestCase):
    """Test suite for CredentialService."""

    def setUp(self, mock_check, mock_generate): # Mocks passed by decorators
        """Set up mocks for each test."""
        self.mock_repo = MagicMock(spec=ICredentialRepository)
        self.service = CredentialService(self.mock_repo)
        # Keep references to mocks if needed for assert counts
        self.mock_generate_hash = mock_generate
        self.mock_check_hash = mock_check
        # Reset mocks for each test
        self.mock_generate_hash.reset_mock()
        self.mock_check_hash.reset_mock()
        self.mock_repo.reset_mock()


    def test_create_credential_success(self, mock_check, mock_generate):
        """Test creating a new credential successfully hashes and saves."""
        name, user, pwd = "new_cred", "new_user", "new_pass"
        expected_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + pwd
        expected_data = {"name": name, "username": user, "password": expected_hash}

        self.mock_repo.get_by_name.return_value = None
        self.mock_repo.save.return_value = None

        result = self.service.create_credential(name, user, pwd)

        self.assertTrue(result)
        self.mock_generate_hash.assert_called_once_with(pwd, method=ANY, salt_length=ANY)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_repo.save.assert_called_once()
        call_args, _ = self.mock_repo.save.call_args
        saved_data = call_args[0]
        self.assertEqual(saved_data["name"], name)
        self.assertEqual(saved_data["username"], user)
        self.assertEqual(saved_data["password"], expected_hash)


    def test_create_credential_already_exists(self, mock_check, mock_generate):
        """Test creating a credential that already exists raises CredentialError."""
        name, user, pwd = "existing_cred", "user", "pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": user, "password": "some_hash"}

        with self.assertRaisesRegex(CredentialError, f"Credential '{name}' already exists."):
            self.service.create_credential(name, user, pwd)

        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_generate_hash.assert_not_called()
        self.mock_repo.save.assert_not_called()


    def test_create_credential_empty_input(self, mock_check, mock_generate):
        """Test creating with empty input raises ValidationError."""
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("", "user", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "", "pass")
        with self.assertRaisesRegex(ValidationError, "cannot be empty"):
            self.service.create_credential("name", "user", "")

        self.mock_repo.get_by_name.assert_not_called()
        self.mock_generate_hash.assert_not_called()
        self.mock_repo.save.assert_not_called()

    def test_delete_credential_success(self, mock_check, mock_generate):
        """Test deleting an existing credential."""
        name = "delete_me"
        self.mock_repo.delete.return_value = True

        result = self.service.delete_credential(name)

        self.assertTrue(result)
        self.mock_repo.delete.assert_called_once_with(name)


    def test_delete_credential_not_found(self, mock_check, mock_generate):
        """Test deleting a non-existent credential."""
        name = "not_found"
        self.mock_repo.delete.return_value = False

        result = self.service.delete_credential(name)

        self.assertFalse(result)
        self.mock_repo.delete.assert_called_once_with(name)


    def test_get_credential_success(self, mock_check, mock_generate):
        """Test retrieving an existing credential (returns hash)."""
        name = "get_me"
        expected_data = {"name": name, "username": "user", "password": "hashed_password"}
        self.mock_repo.get_by_name.return_value = expected_data

        result = self.service.get_credential(name)

        self.assertEqual(result, expected_data)
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_get_credential_not_found(self, mock_check, mock_generate):
        """Test retrieving a non-existent credential."""
        name = "not_found"
        self.mock_repo.get_by_name.return_value = None

        result = self.service.get_credential(name)

        self.assertIsNone(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)


    def test_list_credentials_success(self, mock_check, mock_generate):
        """Test listing credential names."""
        expected_names = ["cred1", "cred2"]
        self.mock_repo.list_credentials.return_value = expected_names

        result = self.service.list_credentials()

        self.assertEqual(result, expected_names)
        self.mock_repo.list_credentials.assert_called_once()


    def test_verify_credential_success(self, mock_check, mock_generate):
        """Test successful password verification."""
        name, pwd_to_check = "mycred", "correct_pass"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + pwd_to_check
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertTrue(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_failure(self, mock_check, mock_generate):
        """Test failed password verification (wrong password)."""
        name, pwd_to_check = "mycred", "wrong_pass"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + "correct_pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_called_once_with(stored_hash, pwd_to_check)


    def test_verify_credential_not_found(self, mock_check, mock_generate):
        """Test verification fails if credential doesn't exist."""
        name, pwd_to_check = "notfound", "pass"
        self.mock_repo.get_by_name.return_value = None

        result = self.service.verify_credential(name, pwd_to_check)

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_not_called()


    def test_verify_credential_empty_password_check(self, mock_check, mock_generate):
        """Test verification fails immediately for empty password check."""
        name = "mycred"
        stored_hash = ("pbkdf2:" if WERKZEUG_AVAILABLE else "plaintext:") + "correct_pass"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": stored_hash}

        result = self.service.verify_credential(name, "")

        self.assertFalse(result)
        # Repo should not be called if password check is empty
        self.mock_repo.get_by_name.assert_not_called()
        self.mock_check_hash.assert_not_called()

    def test_verify_credential_missing_hash(self, mock_check, mock_generate):
        """Test verification fails if stored credential has no password hash."""
        name = "nohash"
        self.mock_repo.get_by_name.return_value = {"name": name, "username": "u", "password": None} # Simulate missing hash

        result = self.service.verify_credential(name, "some_pass")

        self.assertFalse(result)
        self.mock_repo.get_by_name.assert_called_once_with(name)
        self.mock_check_hash.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

########## END FILE: tests/unit/application/test_credential_service.py ##########

