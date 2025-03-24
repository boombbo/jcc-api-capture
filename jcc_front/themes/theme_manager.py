from typing import Dict, Optional, Any
import json
import os
from pathlib import Path
from qtpy.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QTabWidget, QTextEdit
from qtpy import QtCore
from qt_material import apply_stylesheet, QtStyleTools, list_themes, export_theme
import qdarkstyle

# Add QtPy configuration
QT_API = os.environ.get('QT_API', 'pyqt5').lower()
if QT_API not in ['pyqt5', 'pyside2', 'pyqt6', 'pyside6']:
    QT_API = 'pyqt5'

# Get Qt version
QT_VERSION = QtCore.__version__

# ... existing code ...

class ThemeManager(QtStyleTools):
    """Qt Material theme manager with QtPy support"""
    
    def __init__(self, app: QApplication, window: QMainWindow):
        """Initialize theme manager with QtPy support
        
        Args:
            app: QApplication instance
            window: Main window instance
        """
        super().__init__()
        self.app = app
        self.window = window
        self.main = window
        
        # Store Qt binding information
        self.qt_api = QT_API
        self.qt_version = QT_VERSION
        
        # ... rest of existing initialization code ...

    def apply_theme(self, theme_name: str, extra: Optional[Dict] = None, invert_secondary: bool = False) -> None:
        """Apply theme with QtPy compatibility"""
        # Check Qt version for specific handling
        if self.qt_version.startswith('6'):
            # Qt6 specific adjustments
            extra = extra or {}
            extra['qt_version'] = 6
        
        # Apply theme using QtPy compatible widgets
        apply_stylesheet(
            self.app,
            theme=f"{theme_name}.xml",
            invert_secondary=is_light or invert_secondary,
            extra=extra
        )
        
        # ... rest of existing apply_theme code ...

# ... rest of existing code ...
