import tkinter as tk
from src.ui.editor_view import EditorView
from src.ui.runner_view import RunnerView
from src.ui.editor_presenter import EditorPresenter
from src.ui.runner_presenter import RunnerPresenter
from src.infrastructure.persistence import FileSystemCredentialRepository, FileSystemWorkflowRepository
from src.infrastructure.webdrivers import SeleniumWebDriver

def main():
    root = tk.Tk()
    root.title("AUTOCLICK Application")

    # Initialize repositories
    credential_repo = FileSystemCredentialRepository("credentials.json")
    workflow_repo = FileSystemWorkflowRepository("workflows")

    # Initialize WebDriver
    driver = SeleniumWebDriver()

    # Initialize presenters
    editor_presenter = EditorPresenter(None, workflow_repo)
    runner_presenter = RunnerPresenter(None, workflow_repo, driver)

    # Initialize views
    editor_view = EditorView(root, editor_presenter.save_workflow, editor_presenter.load_workflow)
    runner_view = RunnerView(root, runner_presenter.run_workflow, runner_presenter.list_workflows)

    # Set presenters' views
    editor_presenter.view = editor_view
    runner_presenter.view = runner_view

    # Start the Tkinter main loop
    root.mainloop()

    # Quit WebDriver on exit
    driver.quit()

if __name__ == "__main__":
    main()
