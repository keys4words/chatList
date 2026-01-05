"""
Кастомный QTextEdit с обработкой двойного клика для разворачивания окна.
"""
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt


class ResponseTextEdit(QTextEdit):
    """QTextEdit с обработкой двойного клика для разворачивания родительского окна."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
    
    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика - разворачивание родительского окна."""
        if event.button() == Qt.LeftButton and self.parent_dialog:
            # Проверяем, не выделяется ли текст
            if not self.textCursor().hasSelection():
                self.parent_dialog.toggle_maximize()
        
        # Вызываем стандартный обработчик для выделения текста
        super().mouseDoubleClickEvent(event)

