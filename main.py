import os
import sys

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
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

        # Connect buttons to functionality
        self.ui.data_file_browse_button.clicked.connect(self.select_data_file)
        self.ui.analysis_directory_browse_button.clicked.connect(self.select_analysis_directory)
        self.ui.load_from_file_button.clicked.connect(self.load_input_data_to_display)

        # Connecting text changed signals
        self.ui.file_path_line_edit.editingFinished.connect(self.load_input_data_to_display)
        self.ui.analysis_directory_line_edit.editingFinished.connect(self.populate_analyses)
        self.ui.input_data_text_edit.textChanged.connect(self.parse_input_data)

        # Other variables
        self.analysis_containers = {}
        self.parsed_input_data: dict = {}

        # Autosaving/loading on initialization
        self.settings = QSettings("MyCompany", "MyApp")
        self.load_settings()

        # Track all changes to widgets while program is open
        self.track_changes()

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
        self.analysis_containers = {}
        for r_file in os.listdir(analysis_directory):
            if not r_file.endswith(".R"):
                continue
            r_file_path = os.path.normpath(os.path.join(analysis_directory, r_file))
            container = RAnalysisContainer(r_file_path)
            print("Created analysis container for", r_file_path, "with keys:", container.input_keys)
            self.analysis_containers[r_file[:-2]] = container

            # Add analysis widget to ui
            analysis_widget_container = QWidget()
            analysis_widget = Ui_AnalysisWidget()
            analysis_widget.setupUi(analysis_widget_container)
            analysis_widget.analysis_name_label.setText(r_file[:-2])
            self.ui.analysis_selection_layout.insertWidget(self.ui.analysis_selection_layout.count() - 1,
                                                           analysis_widget_container)

            # Connect run button
            analysis_widget.analysis_run_button.clicked.connect(lambda _, c=container: self.run_analysis(c))

    def clear_analyses(self):
        """
        Removes all widgets in the analysis selection layout except the last one (e.g., a spacer).
        """
        self.analysis_containers = {}
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

    def run_analysis(self, analysis_container: RAnalysisContainer):
        required_fields = analysis_container.input_keys
        result = analysis_container.run(
            **{required_fields[i]: v for i, v in enumerate(self.parsed_input_data.values())})

        full_result_string = ""
        for key, value in result.items():
            full_result_string += f"======== {key} ========\n"
            section_string = '\n'.join(value)
            full_result_string += f"{section_string}\n"

        self.ui.output_text_edit.setPlainText(full_result_string)

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
            self.ui.input_data_text_edit.setPlainText("")

    def parse_input_data(self):
        """
        Parses input data as a dictionary where each field name maps to a list of values.
        Stores the result in self.parsed_input_data.
        """
        input_text = self.ui.input_data_text_edit.toPlainText().strip()
        if not input_text:
            self.parsed_input_data = {}
            return  # No data to parse

        lines = input_text.split("\n")
        parsed_data = {}

        for line in lines:
            values = line.split()

            # Ensure headers exist for all values
            while len(parsed_data) < len(values):
                field_name = f"Field {len(parsed_data) + 1}"
                parsed_data[field_name] = []

            # Add values to respective fields
            for i, value in enumerate(values):
                try:
                    converted_value = float(value)
                except ValueError:
                    converted_value = value

                parsed_data[f"Field {i + 1}"].append(converted_value)

        self.parsed_input_data = parsed_data
        self.update_parsed_data_table()

    def update_parsed_data_table(self):
        """
        Updates the tree view UI with the parsed input data.
        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Field Name", "Values"])
        self.ui.parsed_input_tree_view.setModel(model)  # Attach model to the tree view

        for field_name, values in self.parsed_input_data.items():
            str_values = [str(value) for value in values]
            field_item = QStandardItem(field_name)
            values_item = QStandardItem(", ".join(str_values))

            # Make items read-only
            field_item.setFlags(field_item.flags() & ~Qt.ItemIsEditable)
            values_item.setFlags(values_item.flags() & ~Qt.ItemIsEditable)

            # Add tooltip for full text
            values_item.setData(", ".join(str_values), Qt.ToolTipRole)

            model.appendRow([field_item, values_item])

        self.update_enabled_analyses(len(self.parsed_input_data))

    def update_enabled_analyses(self, num_fields: int):
        analysis_names, containers = zip(*self.analysis_containers.items())
        analysis_widgets = [self.ui.analysis_selection_layout.itemAt(i).widget() for i in
                            range(self.ui.analysis_selection_layout.count() - 1)]
        for name, container, widget in zip(analysis_names, containers, analysis_widgets):
            widget.setEnabled(num_fields == len(container.input_keys))

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
