# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Users/Arekusei/Documents/qt/snp.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import yaml
import openpyxl

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QApplication)
from PyQt5 import QtGui, QtWidgets, QtCore
import pandas as pd
from load_data import get_aggregated_patient_data_from_excel
from parse_data import get_info_from_dbSNP
import sys

class ParsingThread(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(list)
    
    def  __init__(self, 
                  patient_snp_list=None, 
                  snp_info_dictionary=None,
                  snp_clinical_dictionary=None,
                  ):
        super().__init__()
        self.patient_snp_list = patient_snp_list
        self.snp_info_dictionary = snp_info_dictionary
        self.snp_clinical_dictionary = snp_clinical_dictionary
        
    def run(self):
        for num, rs_id in enumerate(self.patient_snp_list):
            
            if rs_id in self.snp_info_dictionary.keys():
                allele_data = self.snp_info_dictionary[rs_id]
                final_clinical_info = self.snp_clinical_dictionary[rs_id]
            else:
                allele_data, final_clinical_info = get_info_from_dbSNP(rs_id, MAF_threshold=0.0)
                self.snp_info_dictionary[rs_id] = allele_data
                self.snp_clinical_dictionary[rs_id] = final_clinical_info
            self.mysignal.emit([num, rs_id, 
                                allele_data, 
                                final_clinical_info, 
                                self.snp_info_dictionary, 
                                self.snp_clinical_dictionary])
            
class ComboBoxWithReadOnlyMode(QComboBox):
    
    def __init__(self, parent):
        QComboBox.__init__(self, parent)
        self.readonly = False
        
    def setReadonly(self, value):
        self.readonly = value

    def mousePressEvent(self, event):
        if not self.readonly:
            QComboBox.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        if not self.readonly:
            QComboBox.keyPressEvent(self, event)

    def wheelEvent(self, event):
        if not self.readonly:
            QComboBox.wheelEvent(self, event)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setFixedWidth(1280)
        MainWindow.setFixedHeight(760)

        self.path_to_input_file = None
        self.snp_info_dictionary = {}
        self.snp_clinical_dictionary = {}

        self.centralwidget = QtWidgets.QWidget(MainWindow)

        self.label_agg = QtWidgets.QLabel(self.centralwidget)
        self.label_agg.setGeometry(QtCore.QRect(195, 58, 350, 20))
        self.label_agg.setText(f"Выберите способ агрегации данных")

        self.combo_agg = ComboBoxWithReadOnlyMode(self.centralwidget)
        self.combo_agg.addItems(['Среднее', 'Минимальное', 'Максимальное'])
        self.combo_agg.move(250, 80)
        self.combo_agg.resize(100, 20)
        self.combo_agg.currentTextChanged.connect(self.parametersChanged)

        self.label_browse = QtWidgets.QLabel(self.centralwidget)
        self.label_browse.setGeometry(QtCore.QRect(550, 50, 200, 20))
        self.label_browse.setText(f"Укажите путь до входного файла")

        self.file_browser_btn = QtWidgets.QPushButton(self.centralwidget)
        self.file_browser_btn.clicked.connect(self.select_input_file)
        self.file_browser_btn.setGeometry(QtCore.QRect(600, 70, 100, 30))

        self.label_depth = QtWidgets.QLabel(self.centralwidget)
        self.label_depth.setGeometry(QtCore.QRect(900, 58, 150, 20))
        self.label_depth.setText('Задайте порог покрытия')

        self.lineEdit_depth = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_depth.setGeometry(QtCore.QRect(1060, 55, 50, 31))
        self.lineEdit_depth.textChanged.connect(self.parametersChanged)

        
        self.pushButton_update = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_update.setGeometry(QtCore.QRect(520, 150, 260, 20))
        self.pushButton_update.clicked.connect(self.updatedata)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(550, 200, 200, 60))
        self.pushButton.clicked.connect(self.onActivated)
        self.pushButton.setEnabled(False)

        self.label_maf = QtWidgets.QLabel(self.centralwidget)
        self.label_maf.setGeometry(QtCore.QRect(910, 130, 120, 20))
        self.label_maf.setText('Задайте порог MAF')

        self.lineEdit_maf = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_maf.setGeometry(QtCore.QRect(1040, 125, 50, 31))

        self.pushButton_maf = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_maf.setGeometry(QtCore.QRect(900, 200, 200, 61))
        self.pushButton_maf.clicked.connect(self.filter_info)
        self.pushButton_maf.setEnabled(False)

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(150, 260, 981, 411))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.list_0 = QtWidgets.QLabel(self.verticalLayoutWidget)

        self.verticalLayout.addWidget(self.list_0)
        self.textEdit = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.verticalLayout.addWidget(self.textEdit)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1113, 26))

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.label_select_patient = QLabel(self.centralwidget)
        self.label_select_patient.setGeometry(202, 130, 500, 20)
        self.label_select_patient.setText(f"Выберите пациента для анализа")

        self.combo = ComboBoxWithReadOnlyMode(self.centralwidget)
        self.combo.move(200, 155)
        self.combo.resize(200, 25)
        self.combo.currentTextChanged.connect(lambda x: self.pushButton_maf.setEnabled(False))
        # self.combo.activated[str].connect(self.onPatientSelected)

        # self.request_status = QLabel(self.centralwidget)
        # self.request_status.setGeometry(540, 130, 500, 20)
        self.request_status = self.textEdit
        self.request_status.setText(f"{' '*3}Приветствуем вас в SNP Analyzer!")
        self.request_status.setVisible(True)
        
        self.progress = QtWidgets.QProgressBar(self.centralwidget)
        self.progress.setGeometry(180, 220, 280, 20)
        self.progress.setVisible(False)

    def parametersChanged(self):
        if self.path_to_input_file is not None:
            self.pushButton_update.setEnabled(True)
            self.pushButton.setEnabled(False)
    
    def updatedata(self):
        self.combo.clear() 
        self.pushButton_update.setEnabled(False)
        self.load_input_file(self.path_to_input_file)

    def select_input_file(self): 
        self.select_input_file_dialog = QtWidgets.QFileDialog(self.centralwidget)
        self.select_input_file_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.select_input_file_dialog.setNameFilter("Excel tables (*.xlsx *.xls)")
        self.select_input_file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if self.select_input_file_dialog.exec():
            self.path_to_input_file = self.select_input_file_dialog.selectedFiles()[-1]
            self.load_input_file(self.path_to_input_file)

    def load_input_file(self, path_to_input_file):
        
        self.combo.clear() 
        
        try:
            seq_threshhold_depth = float(self.lineEdit_depth.text())
        except ValueError:
            seq_threshhold_depth = 10 
            self.lineEdit_depth.setText('10')
            self.pushButton_update.setEnabled(False)

        df, unique_patients = get_aggregated_patient_data_from_excel(path_to_input_file=path_to_input_file,
                                                                     seq_threshhold_depth=seq_threshhold_depth,
                                                                     aggregation_method=self.combo_agg.currentText(),
                                                                     )
        self.df = df
        self.unique_patients = sorted(unique_patients, key=lambda x: int(x.split('_')[-1]))
        self.combo.addItems (self.unique_patients) 
        self.pushButton.setEnabled(True)
        self.textEdit.setText(f'Загружены данные по пути:\n{path_to_input_file}')

    def filter_info(self):
        patient_id = self.combo.currentText()
        patient_info = self.df[patient_id]
        patient_snp_list = list(patient_info[patient_info>0].index)
        self.allele_data_list = []
        
        try:
            self.MAF_threshold = float(self.lineEdit_maf.text())
        except ValueError:
            print("AHTUNG!")
            self.lineEdit_maf.setText('0.0')
            self.MAF_threshold = 0.0

        for rs_id in patient_snp_list:
            allele_data = self.snp_info_dictionary[rs_id]
            final_clinical_info = self.snp_clinical_dictionary[rs_id]

            if len(allele_data) and float(allele_data[0].split()[0].split('=')[-1]) >= self.MAF_threshold:
                mafs = [float(entry.split('=')[-1].split()[0]) for entry in allele_data]
                mean_maf = round(sum(mafs)/len(mafs), 5)
                if final_clinical_info is None: final_clinical_info = ''
                self.allele_data_list.append((rs_id, f"average MAF = {mean_maf} from {len(mafs)} sources {final_clinical_info}"))
        data_to_print = [': '.join(snp_) for snp_ in self.allele_data_list]
        self.textEdit.setText('\n'.join(data_to_print))
       
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SNP Analyzer"))
        self.pushButton.setText(_translate("MainWindow", "Начать поиск"))
        self.pushButton_update.setText(_translate("MainWindow", "Обновить параметры обработки данных"))
        self.file_browser_btn.setText(_translate("MainWindow", "Выбрать..."))
        self.pushButton_maf.setText(_translate("MainWindow", "Фильтровать"))
        self.lineEdit_maf.setText(_translate("MainWindow", "0.3"))
        self.lineEdit_depth.setText(_translate("MainWindow", "10"))
        self.list_0.setText(' ')
        self.pushButton_update.setEnabled(False)

    def onActivated(self):
        self.pushButton.setEnabled(False)
        self.combo.setReadonly(True)
        self.combo_agg.setReadonly(True)
        self.lineEdit_depth.setEnabled(False)
        self.lineEdit_maf.setEnabled(False)
        
        patient_id = self.combo.currentText()
        patient_info = self.df[patient_id]
        patient_snp_list = list(patient_info[patient_info>0].index)
        self.allele_data_list = []
        
        self.progress.setRange(0, len(patient_snp_list))
        self.progress.setValue(0)
        self.progress.setVisible(True)
        try:
            self.MAF_threshold = float(self.lineEdit_maf.text())
        except ValueError:
            print("AHTUNG!")
            self.lineEdit_maf.setText('0.0')
            self.MAF_threshold = 0.0
        
        if not len(patient_snp_list): 
            self.textEdit.setText('Ничего не найдено по заданным критериям')
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
            self.progress.setVisible(True)
            self.combo.setReadonly(False)
            self.file_browser_btn.setEnabled(True)
            self.combo_agg.setReadonly(False)
            self.lineEdit_depth.setEnabled(True)
            self.pushButton.setEnabled(True)
        else:
            self.request_status.setVisible(True)
            self.request_status.setText(f"parsing info on {patient_snp_list[0]} from dbSNP")
            
            
            self.mythread = ParsingThread(patient_snp_list, self.snp_info_dictionary, self.snp_clinical_dictionary)    # Создаем экземпляр класса
            # self.mythread.started.connect(self.on_started)
            self.mythread.finished.connect(self.on_finished)
            self.mythread.mysignal.connect(self.on_change, QtCore.Qt.QueuedConnection)
            self.mythread.start() 
            self.file_browser_btn.setEnabled(False)
        
    def on_change(self, emmited_list):
        num, rs_id, allele_data, final_clinical_info, updated_info_dictionary, updated_clinical_dictionary = emmited_list
        self.progress.setValue(num+1)
        self.request_status.setText(f"parsing info on {rs_id} from dbSNP")
        # self.request_status.adjustSize()
        if len(allele_data) and float(allele_data[0].split()[0].split('=')[-1]) >= self.MAF_threshold:
            mafs = [float(entry.split('=')[-1].split()[0]) for entry in allele_data]
            mean_maf = round(sum(mafs)/len(mafs), 5)
            if final_clinical_info is None: final_clinical_info = ''
            self.allele_data_list.append((rs_id, f"average MAF = {mean_maf} from {len(mafs)} sources {final_clinical_info}"))
        self.snp_info_dictionary = updated_info_dictionary
        self.snp_clinical_dictionary = updated_clinical_dictionary
        
    def on_finished(self):      # Вызывается при завершении потока
        
        self.progress.setMaximum(1)
        self.progress.setValue(1)
        data_to_print = [': '.join(snp_) for snp_ in self.allele_data_list]
        self.textEdit.setText('\n'.join(data_to_print))
        # self.request_status.setText(f"{' '*20}completed")
        self.combo.setReadonly(False)
        self.file_browser_btn.setEnabled(True)
        self.combo_agg.setReadonly(False)
        self.lineEdit_depth.setEnabled(True)
        self.lineEdit_maf.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.pushButton_maf.setEnabled(True)
        # self.progress.setVisible(False)
        # self.request_status.setVisible(False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
