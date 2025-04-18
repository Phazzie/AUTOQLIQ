"""UI factory for creating common UI components."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any, Optional, Union

from src.core.exceptions import UIError
from src.ui.common.service_provider import ServiceProvider


class UIFactory:
    """Factory for creating common UI components.

    This class provides methods for creating common UI components with consistent
    styling and behavior. It primarily uses ttk widgets for a modern look.
    """

    def __init__(self, service_provider: Optional[ServiceProvider] = None):
        """Initialize a new UIFactory.

        Args:
            service_provider: The service provider for dependency injection.
        """
        self.service_provider = service_provider or ServiceProvider()

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
