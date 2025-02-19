import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QTextEdit, QCheckBox

from r_container import RAnalysisContainer
from ui.analysis_widget_init import Ui_AnalysisWidget
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

        self.ui.analysis_directory_line_edit.editingFinished.connect(self.populate_analyses)

        # Track all changes to widgets while program is open
        self.track_changes()

        # Storage for analysis containers
        self.analysis_containers = []

    def track_changes(self):
        for widget in self.findChildren((QLineEdit, QTextEdit)):
            widget.textChanged.connect(lambda _, w=widget: self.settings.setValue(w.objectName(), w.text()))
        for checkbox in self.findChildren(QCheckBox):
            checkbox.stateChanged.connect(lambda _, c=checkbox: self.settings.setValue(c.objectName(), c.isChecked()))

    def populate_analyses(self):
        analysis_directory = self.ui.analysis_directory_line_edit.text()
        if not os.path.exists(analysis_directory):
            self.clear_analyses()
            return

        # Create analysis containers for each r file in the selected directory
        self.analysis_containers = []
        for r_file in os.listdir(analysis_directory):
            if not r_file.endswith(".R"):
                continue
            r_file_path = os.path.normpath(os.path.join(analysis_directory, r_file))
            container = RAnalysisContainer(r_file_path)
            print("Created analysis container for", r_file_path, "with keys:", container.input_keys)
            self.analysis_containers.append(container)

            # Add analysis widget to ui
            analysis_widget_container = QWidget()
            analysis_widget = Ui_AnalysisWidget()
            analysis_widget.setupUi(analysis_widget_container)
            analysis_widget.analysis_name_label.setText(r_file[:-2])
            self.ui.analysis_selection_layout.insertWidget(self.ui.analysis_selection_layout.count() - 1,
                                                           analysis_widget_container)

    def clear_analyses(self):
        """
        Removes all widgets in the analysis selection layout except the last one (e.g., a spacer).
        """
        self.analysis_containers = []
        layout = self.ui.analysis_selection_layout
        count = layout.count()

        # Remove all widgets except the last one
        for i in reversed(range(count - 1)):  # Leave the last widget
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    layout.removeWidget(widget)
                    widget.deleteLater()  # Properly delete the widget

    def select_data_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        self.ui.file_path_line_edit.setText(file_path)

    def select_analysis_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.ui.analysis_directory_line_edit.setText(dir_path)
        self.populate_analyses()

    def load_input_data_to_display(self):
        try:
            with open(self.ui.file_path_line_edit.text(), "r") as f:
                data = f.read()
                self.ui.input_data_text_edit.setPlainText(data)
        except FileNotFoundError:
            pass

    def load_settings(self):
        for widget in self.findChildren((QLineEdit, QTextEdit)):
            widget.setText(self.settings.value(widget.objectName(), ""))
            if widget.objectName() == "analysis_directory_line_edit":
                self.populate_analyses()
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(self.settings.value(checkbox.objectName(), False, type=bool))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
