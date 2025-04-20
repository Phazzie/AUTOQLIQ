from abc import ABC, abstractmethod
from typing import Dict, Any

from src.core.interfaces import IAction, IWebDriver
from src.core.action_result import ActionResult
import logging
from src.core.exceptions import ValidationError, ActionError

# Refactored to alias the ActionBase from core/actions/base.py
from src.core.actions.base import ActionBase

# DEPRECATED: This module will be removed once all references point to src.core.actions.base
