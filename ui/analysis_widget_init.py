# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\analysis_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AnalysisWidget(object):
    def setupUi(self, AnalysisWidget):
        AnalysisWidget.setObjectName("AnalysisWidget")
        AnalysisWidget.resize(400, 147)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(AnalysisWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.analysis_run_button = QtWidgets.QPushButton(AnalysisWidget)
        self.analysis_run_button.setObjectName("analysis_run_button")
        self.horizontalLayout.addWidget(self.analysis_run_button)
        self.analysis_name_label = QtWidgets.QLabel(AnalysisWidget)
        self.analysis_name_label.setObjectName("analysis_name_label")
        self.horizontalLayout.addWidget(self.analysis_name_label)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(AnalysisWidget)
        QtCore.QMetaObject.connectSlotsByName(AnalysisWidget)

    def retranslateUi(self, AnalysisWidget):
        _translate = QtCore.QCoreApplication.translate
        AnalysisWidget.setWindowTitle(_translate("AnalysisWidget", "Form"))
        self.analysis_run_button.setText(_translate("AnalysisWidget", "Run"))
        self.analysis_name_label.setText(_translate("AnalysisWidget", "NO_NAME"))
