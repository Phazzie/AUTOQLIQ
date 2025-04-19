import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Fix missing imports
import tkinter as tk
from typing import Optional, Dict, Any, List, Callable

# Make these available in the global namespace
sys.modules['__main__'].__dict__['Optional'] = Optional
sys.modules['__main__'].__dict__['Dict'] = Dict
sys.modules['__main__'].__dict__['Any'] = Any
sys.modules['__main__'].__dict__['List'] = List
sys.modules['__main__'].__dict__['Callable'] = Callable
sys.modules['__main__'].__dict__['tk'] = tk

# Import and run the refactored UI
try:
    print("Trying to run main_ui_refactored_v4.py...")
    exec(open("src/main_ui_refactored_v4.py").read())
except Exception as e:
    print(f"Error with v4: {e}")
    print("Trying v3...")
    try:
        exec(open("src/main_ui_refactored_v3.py").read())
    except Exception as e:
        print(f"Error with v3: {e}")
        print("Trying v2...")
        try:
            exec(open("src/main_ui_refactored_v2.py").read())
        except Exception as e:
            print(f"Error with v2: {e}")
            print("Trying v1...")
            try:
                exec(open("src/main_ui_refactored.py").read())
            except Exception as e:
                print(f"Error with v1: {e}")
                print("All attempts failed.")
