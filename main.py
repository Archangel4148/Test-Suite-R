import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QTextEdit, QCheckBox

from ui.main_window_init import Ui_MainWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Autosaving/loading on initialization
        self.settings = QSettings("MyCompany", "MyApp")
        self.load_settings()

        # Connect buttons to functionality
        self.ui.data_file_browse_button.clicked.connect(self.select_data_file)
        self.ui.analysis_directory_browse_button.clicked.connect(self.select_analysis_directory)
        self.ui.load_from_file_button.clicked.connect(self.load_to_display)

        # Track all changes to widgets while program is open
        self.track_changes()

    def track_changes(self):
        for widget in self.findChildren((QLineEdit, QTextEdit)):
            widget.textChanged.connect(lambda _, w=widget: self.settings.setValue(w.objectName(), w.text()))
        for checkbox in self.findChildren(QCheckBox):
            checkbox.stateChanged.connect(lambda _, c=checkbox: self.settings.setValue(c.objectName(), c.isChecked()))

    def populate_analyses(self):
        pass

    def select_data_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        self.ui.file_path_line_edit.setText(file_path)

    def select_analysis_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.ui.analysis_directory_line_edit.setText(dir_path)

    def load_to_display(self):
        try:
            with open(self.ui.file_path_line_edit.text(), "r") as f:
                data = f.read()
                self.ui.data_text_edit.setPlainText(data)

        except FileNotFoundError:
            pass

    def load_settings(self):
        for widget in self.findChildren((QLineEdit, QTextEdit)):
            widget.setText(self.settings.value(widget.objectName(), ""))
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(self.settings.value(checkbox.objectName(), False, type=bool))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
