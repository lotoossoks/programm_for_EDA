import sys
import shutil
import sqlite3
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QTableWidgetItem, QListView


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def proc_all_var(df):
    """
    Рассчитывает все нужные метрики по DataFrame
    :param df: DataFrame
    :return: dict всеми нажными метриками по DataFrame
    """
    if os.path.exists('folder'):
        shutil.rmtree('folder')
    os.mkdir("folder")
    final_dict = {'DataFrame': {}}
    final_dict['DataFrame']['Названия столбцов'] = list(df.columns)
    final_dict['DataFrame']['Количество столбцов'] = len(final_dict['DataFrame']['Названия столбцов'])
    final_dict['DataFrame']['Названия и тип столбцов'] = df.dtypes
    final_dict['DataFrame']['Количество строк'] = df.shape[0]
    final_dict['DataFrame']['Количество пропущенных клеток'] = df.isnull().sum().sum()
    final_dict['DataFrame']['Процент пропущенных клеток'] = 100 * final_dict['DataFrame'][
        'Количество пропущенных клеток'] / (
                                                                    final_dict['DataFrame']['Количество строк'] *
                                                                    final_dict['DataFrame']['Количество столбцов'])
    final_dict['DataFrame']['Количество повторяющихся строк'] = final_dict['DataFrame']['Количество строк'] - \
                                                                df.drop_duplicates().shape[0]
    final_dict['DataFrame']['Процент повторяющихся строк'] = 100 * final_dict['DataFrame'][
        'Количество повторяющихся строк'] / final_dict['DataFrame'][
                                                                 'Количество строк']
    final_dict['variables'] = {}
    for name_col in final_dict['DataFrame']['Названия столбцов']:
        final_dict['variables'][name_col] = {}
        final_dict['variables'][name_col]['Тип столбца'] = final_dict['DataFrame']['Названия и тип столбцов'][name_col]
        final_dict['variables'][name_col]['Количество уникальных значений'] = len(df[name_col].unique())
        final_dict['variables'][name_col]['Количество пропущенных значений'] = df[name_col].isnull().sum()
        final_dict['variables'][name_col]['Процент пропущенных значений'] = 100 * df[name_col].isnull().sum() / \
                                                                            final_dict['DataFrame'][
                                                                                'Количество строк']
        if final_dict['variables'][name_col]['Тип столбца'] in ['float64', 'int64']:
            final_dict['variables'][name_col]['Среднее'] = df[name_col].mean()
            final_dict['variables'][name_col]['Минимальное'] = df[name_col].min()
            final_dict['variables'][name_col]['5 перцентиль'] = np.percentile(df[name_col], 5)
            final_dict['variables'][name_col]['1 квартиль'] = np.percentile(df[name_col], 25)
            final_dict['variables'][name_col]['Медиана'] = np.percentile(df[name_col], 50)
            final_dict['variables'][name_col]['3 квартиль'] = np.percentile(df[name_col], 75)
            final_dict['variables'][name_col]['95 перцентиль'] = np.percentile(df[name_col], 95)
            final_dict['variables'][name_col]['Максимальное'] = df[name_col].max()
            final_dict['variables'][name_col]['Количество нулей'] = final_dict['DataFrame']['Количество строк'] - df[
                name_col].count()
            final_dict['variables'][name_col]['Процент нулей'] = 100 * final_dict['variables'][name_col][
                'Количество нулей'] / final_dict['DataFrame'][
                                                                     'Количество строк']
            final_dict['variables'][name_col]['Стандартное отклонение'] = df[name_col].std()
            final_dict['variables'][name_col]['Сумма'] = df[name_col].sum()
            final_dict['variables'][name_col]['Наиболее повторяющиеся значения'] = df[
                                                                                       name_col].value_counts().sort_values(
                ascending=False).iloc[0:5]
            fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(10, 8))
            sns.boxplot(data=df[name_col], ax=ax1)
            sns.histplot(data=df[name_col], ax=ax2, bins=30)
            ax1.set_title(f"{name_col}")
            plt.savefig(f'folder/{name_col}.png')
            plt.close()
    fig, (ax1) = plt.subplots(figsize=(10, 10))
    sns.heatmap(data=df[list(filter(lambda x: final_dict['variables'][x]['Тип столбца'] in ['float64', 'int64'],
                                    final_dict['DataFrame']['Названия столбцов']))].corr(), ax=ax1, cmap="crest")
    plt.savefig(f'folder/corr.png', dpi=75)
    plt.close()
    return final_dict


class Picture(QMainWindow):
    """
    Класс для вывода графика в отдельном окне

    Атрибуты
    --------
    image: QLabel
        Атрибут класса QLabel
    pixmap: QPixmap
        Атрибут класса QPixmap
    path: str
        Путь до графика, который нужно вывести (в папке folder)
    """

    def __init__(self, path):
        super().__init__()
        self.image = None
        self.pixmap = None
        self.path = path
        self.initUI()

    def initUI(self):
        """
        Вывод графика в отдельном окне
        """
        self.setWindowTitle('Отображение графика')
        self.pixmap = QPixmap(self.path)
        self.setGeometry(200, 200, self.pixmap.width(), self.pixmap.height())
        self.image = QLabel(self)
        self.image.resize(self.pixmap.size())
        self.image.setPixmap(self.pixmap)


class OutDataBase(QMainWindow):
    """
    Класс для определения какая именно табоица нужна из файла базы данныи превращения в DataFrame

    Атрибуты
    --------
    parent: объект родительского класса MainWindow
        Нужно, чтобы обращатся к атрибутам и методам родительского класса
    path: str
        Путь до базы данных

    """

    def __init__(self, parent, path):
        super().__init__()
        self.parent = parent
        self.path = path
        self.initUI()

    def initUI(self):
        """
        Берет базу данных при помощи path, создается новое окно, пользователь определяет какая таблица нужна
        """
        self.setObjectName("MainWindow")
        self.setGeometry(80, 80, 1649, 982)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(50, 10, 931, 831))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.comboTab = QtWidgets.QComboBox(self.centralwidget)
        self.comboTab.setGeometry(QtCore.QRect(1010, 20, 221, 31))
        self.comboTab.setObjectName("comboTab")
        self.pushNext = QtWidgets.QPushButton(self.centralwidget)
        self.pushNext.setGeometry(QtCore.QRect(1240, 20, 121, 31))
        self.pushNext.setObjectName("pushNext")
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1649, 18))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushNext.setText(_translate("MainWindow", "PushButton"))
        self.setWindowTitle('Отображение Базы Данных')
        con = sqlite3.connect(self.path)
        self.cur = con.cursor()
        tables = list(
            map(lambda x: x[0], self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()))
        titles = []
        for i in range(len(tables)):
            titles.append([x[1] for x in self.cur.execute(f'PRAGMA table_info({tables[i]})').fetchall()])
        titles = list(map(lambda x: x + [""] * (len(max(titles, key=len)) - len(x)), titles))
        self.tableWidget.setColumnCount(len(tables))
        self.tableWidget.setRowCount(len(max(titles, key=len)))
        self.tableWidget.setHorizontalHeaderLabels(tables)
        for i in range(len(tables)):
            for j in range(len(max(titles, key=len))):
                self.tableWidget.setItem(j, i, QTableWidgetItem(str(titles[i][j])))
        for name in tables:
            self.comboTab.addItem(name)
        self.pushNext.clicked.connect(self.push_next_f)

    def push_next_f(self):
        """
        Преобразвание выбранной табицы в DataFrame
        :return: DataFrame
        """
        base_titles = [x[1] for x in self.cur.execute(f'PRAGMA table_info({self.comboTab.currentText()})').fetchall()]
        data = self.cur.execute(f"SELECT * FROM {self.comboTab.currentText()}").fetchall()
        self.parent.df = pd.DataFrame(data, columns=base_titles)
        self.close()
        self.parent.show()
        self.parent.make_dataframe()


class MainWindow(QMainWindow):
    """
    Базовый класс. Реализация программы для предобработки табличных форматов данных

    Атрибуты
    --------
    df: DataFrame
        DataFrame, который был получен из загружденного файла
    df_copy: DataFrame
        Копия df
    outdb: OutDataBase
        Экземпляр класса OutDataBase
    var_dict: dict
        Словарь, в котором есть все нужные метрики по DataFrame
    pict: Picture
        Экземпляр класса Picture
    listview: QListView
        Экземпляр класса QListView
    model: QStandardItemModel()
        Экземпляр класса QStandardItemModel()

    Методы
    ------
    take_file() :
        Получает имя файла, в зависимости от типа данных класса превращает в DataFrame
    make_dataframe() :
        Получает DataFrame, при помощи фунцкии превращает в список всех нужных метрик
    design_main_window() :
        Загружает дизайн основного окна, вызывает исполнение всех дейстивий в вкладках этого окна
    string_dataframe() :
        Создает на вкладке StringDF таблицу с 5 случайными строками
    dataframe() :
        Выводит на вкладку DataFrame всю нужную информацию по DataFrame в целом
    variables() :
        Выводит на вкладку Variables всю нужную информацию по каждой переменной в отдельности и возможность
        отображения графиков для выбранного столбца
    change_button_status() :
        Реализация возможность отображения графиков для выбранного столбца (boxplot, hisplot)
    correlation() :
        Вывод графика корреляции и при нажатии кнопки возможность вывода scatter plot 2-х выбранных графиков
    make_scatter() :
        Реализация возможности вывода scatter plot 2-х выбранных графиков
    tab_widget_changed() :
        Действия привязанные на смену вкладки
    clear_dataframe() :
        Функции для очистики и последующего сохранения DataFrame в выбранный формат данных
    drop_dulicates() :
        Удаление дублей в DataFrame
    slider_changed() :
        Функция зависящая от изменения 2-х слайдеров, меняет 2 label в зависимости от слайдера
    del_data() :
        Удаление выбросов по квартилям, которые зависят от значений, которые выбраны на слайдерах
    save_dataframe():
        Сохранение DataFrame в выбранный формат
    """

    def __init__(self):
        super().__init__()
        self.df = None
        self.take_file()

    def take_file(self):
        """
        Получает имя файла, в зависимости от типа данных класса превращает в DataFrame
        :return: DataFrame из полученного файла
        """
        fname = QFileDialog.getOpenFileName(self, 'Выбрать файл', '',
                                            'Таблица (*.csv);; '
                                            'Таблица (*.xlsx);; '
                                            'Базы данных (*.db);;'
                                            'Базы данных (*.sqlite);;')[0]
        if fname.split('.')[-1] in ['db', 'sqlite']:
            self.outdb = OutDataBase(self, fname)
            self.outdb.show()
        elif fname.split('.')[-1] == 'csv':
            self.df = pd.read_csv(fname, sep=',', low_memory=False)
            self.make_dataframe()
        else:
            self.df = pd.read_excel(fname, sep=',', low_memory=False)
            self.make_dataframe()

    def make_dataframe(self):
        """
        Получает DataFrame, при помощи фунцкии превращает в список всех нужных метрик
        :return: список всех нужных метрик
        """
        self.df_copy = self.df.copy()
        self.var_dict = proc_all_var(self.df)
        self.design_main_window()

    def design_main_window(self):
        """
        Загружает дизайн основного окна, вызывает исполнение всех дейстивий в вкладках этого окна
        """
        self.setObjectName("MainWindow")
        self.resize(1168, 1248)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.TabWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.TabWidget.setObjectName("TabWidget")
        self.Sample = QtWidgets.QWidget()
        self.Sample.setObjectName("Sample")
        self.tableWidget = QtWidgets.QTableWidget(self.Sample)
        self.tableWidget.setGeometry(QtCore.QRect(0, 90, 1281, 1081))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.label = QtWidgets.QLabel(self.Sample)
        self.label.setGeometry(QtCore.QRect(0, 0, 631, 91))
        self.label.setObjectName("label")
        self.TabWidget.addTab(self.Sample, "")
        self.DataFrame = QtWidgets.QWidget()
        self.DataFrame.setObjectName("DataFrame")
        self.labelDataFrame = QtWidgets.QLabel(self.DataFrame)
        self.labelDataFrame.setGeometry(QtCore.QRect(0, 0, 671, 81))
        self.labelDataFrame.setObjectName("labelDataFrame")
        self.DataFrameTextEdit = QtWidgets.QTextEdit(self.DataFrame)
        self.DataFrameTextEdit.setEnabled(True)
        self.DataFrameTextEdit.setGeometry(QtCore.QRect(0, 120, 1471, 1041))
        self.DataFrameTextEdit.setMaximumSize(QtCore.QSize(1471, 1131))
        self.DataFrameTextEdit.setObjectName("DataFrameTextEdit")
        self.DataFrameTextEdit.raise_()
        self.labelDataFrame.raise_()
        self.TabWidget.addTab(self.DataFrame, "")
        self.Variables = QtWidgets.QWidget()
        self.Variables.setObjectName("Variables")
        self.comboBox = QtWidgets.QComboBox(self.Variables)
        self.comboBox.setGeometry(QtCore.QRect(10, 60, 311, 31))
        self.comboBox.setObjectName("comboBox")
        self.labelVariables = QtWidgets.QLabel(self.Variables)
        self.labelVariables.setEnabled(True)
        self.labelVariables.setGeometry(QtCore.QRect(0, -20, 1011, 81))
        self.labelVariables.setObjectName("labelVariables")
        self.VariablesTextEdit = QtWidgets.QTextEdit(self.Variables)
        self.VariablesTextEdit.setEnabled(True)
        self.VariablesTextEdit.setGeometry(QtCore.QRect(0, 120, 1291, 1051))
        self.VariablesTextEdit.setObjectName("VariablesTextEdit")
        self.comboBox.raise_()
        self.VariablesTextEdit.raise_()
        self.labelVariables.raise_()
        self.TabWidget.addTab(self.Variables, "")
        self.Correlations = QtWidgets.QWidget()
        self.Correlations.setObjectName("Correlations")
        self.labelCorrelations = QtWidgets.QLabel(self.Correlations)
        self.labelCorrelations.setEnabled(True)
        self.labelCorrelations.setGeometry(QtCore.QRect(0, 0, 591, 81))
        self.labelCorrelations.setObjectName("labelCorrelations")
        self.imageHeatmap = QtWidgets.QLabel(self.Correlations)
        self.imageHeatmap.setGeometry(QtCore.QRect(20, 150, 631, 551))
        self.imageHeatmap.setObjectName("imageHeatmap")
        self.comboOx = QtWidgets.QComboBox(self.Correlations)
        self.comboOx.setGeometry(QtCore.QRect(790, 30, 141, 31))
        self.comboOx.setObjectName("comboOx")
        self.comboOy = QtWidgets.QComboBox(self.Correlations)
        self.comboOy.setGeometry(QtCore.QRect(970, 30, 151, 31))
        self.comboOy.setObjectName("comboOy")
        self.ScatterButton = QtWidgets.QPushButton(self.Correlations)
        self.ScatterButton.setGeometry(QtCore.QRect(870, 80, 171, 41))
        self.ScatterButton.setObjectName("ScatterButton")
        self.imageScatter = QtWidgets.QLabel(self.Correlations)
        self.imageScatter.setGeometry(QtCore.QRect(760, 150, 521, 551))
        self.imageScatter.setObjectName("imageScatter")
        self.imageHeatmap.raise_()
        self.comboOx.raise_()
        self.comboOy.raise_()
        self.ScatterButton.raise_()
        self.imageScatter.raise_()
        self.labelCorrelations.raise_()
        self.TabWidget.addTab(self.Correlations, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.dropButton = QtWidgets.QPushButton(self.tab)
        self.dropButton.setGeometry(QtCore.QRect(30, 100, 231, 41))
        self.dropButton.setObjectName("dropButton")
        self.minSlider = QtWidgets.QSlider(self.tab)
        self.minSlider.setGeometry(QtCore.QRect(400, 220, 160, 16))
        self.minSlider.setMaximum(50)
        self.minSlider.setOrientation(QtCore.Qt.Horizontal)
        self.minSlider.setObjectName("minSlider")
        self.delButton = QtWidgets.QPushButton(self.tab)
        self.delButton.setGeometry(QtCore.QRect(470, 250, 191, 41))
        self.delButton.setObjectName("delButton")
        self.minQuart = QtWidgets.QLabel(self.tab)
        self.minQuart.setGeometry(QtCore.QRect(360, 210, 41, 31))
        self.minQuart.setObjectName("minQuart")
        self.maxQuart = QtWidgets.QLabel(self.tab)
        self.maxQuart.setGeometry(QtCore.QRect(730, 210, 51, 41))
        self.maxQuart.setObjectName("maxQuart")
        self.maxSlider = QtWidgets.QSlider(self.tab)
        self.maxSlider.setGeometry(QtCore.QRect(560, 220, 160, 16))
        self.maxSlider.setMinimum(50)
        self.maxSlider.setMaximum(100)
        self.maxSlider.setSliderPosition(100)
        self.maxSlider.setOrientation(QtCore.Qt.Horizontal)
        self.maxSlider.setObjectName("maxSlider")
        self.label_9 = QtWidgets.QLabel(self.tab)
        self.label_9.setGeometry(QtCore.QRect(290, 170, 261, 41))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.tab)
        self.label_10.setGeometry(QtCore.QRect(590, 170, 401, 41))
        self.label_10.setObjectName("label_10")
        self.saveButton = QtWidgets.QPushButton(self.tab)
        self.saveButton.setGeometry(QtCore.QRect(900, 210, 191, 41))
        self.saveButton.setObjectName("saveButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 160, 261, 1011))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 591, 81))
        self.label_2.setObjectName("label_2")
        self.TabWidget.addTab(self.tab, "")
        self.horizontalLayout.addWidget(self.TabWidget)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1168, 18))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        self.TabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow",
                                      "<html><head/><body><p><span style=\" font-size:22pt; font-weight:600;\">Random 5 dataframe lines</span></p></body></html>"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Sample), _translate("MainWindow", "StringDF"))
        self.labelDataFrame.setText(_translate("MainWindow",
                                               "<html><head/><body><p><span style=\" font-size:20pt; font-weight:600;\">Information about all dataframe</span></p></body></html>"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.DataFrame), _translate("MainWindow", "DataFrame"))
        self.labelVariables.setText(_translate("MainWindow",
                                               "<html><head/><body><p><span style=\" font-size:20pt; font-weight:600;\">Information about each variable</span></p></body></html>"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Variables), _translate("MainWindow", "Variables"))
        self.labelCorrelations.setText(_translate("MainWindow",
                                                  "<html><head/><body><p><span style=\" font-size:20pt; font-weight:600;\">Correlations</span></p></body></html>"))
        self.imageHeatmap.setText(_translate("MainWindow", "TextLabel"))
        self.ScatterButton.setText(_translate("MainWindow", "Создать Scatter plot"))
        self.imageScatter.setText(_translate("MainWindow", "TextLabel"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.Correlations),
                                  _translate("MainWindow", "Correlations"))
        self.dropButton.setText(_translate("MainWindow", "Удалить дубликаты"))
        self.delButton.setText(_translate("MainWindow", "Удалить выбросы"))
        self.minQuart.setText(_translate("MainWindow", "0"))
        self.maxQuart.setText(_translate("MainWindow", "100"))
        self.label_9.setText(_translate("MainWindow", "Удаляются квартили за слайдером"))
        self.label_10.setText(_translate("MainWindow", "Удаляются картили перед слайдером"))
        self.saveButton.setText(_translate("MainWindow", "Сохранить DataFrame"))
        self.label_2.setText(_translate("MainWindow",
                                        "<html><head/><body><p><br/><span style=\" font-size:20pt; font-weight:600;\">Clearing the dataframe</span></p></body></html>"))
        self.TabWidget.setTabText(self.TabWidget.indexOf(self.tab), _translate("MainWindow", "ClearDataFrame"))
        self.showMaximized()

        self.string_dataframe()
        self.dataframe()
        self.variables()
        self.correlation()
        self.clear_dataframe()
        self.show()

    def string_dataframe(self):
        """
        Создает на вкладке StringDF таблицу с 5 случайными строками
        """
        self.tableWidget.setColumnCount(len(self.var_dict['DataFrame']['Названия столбцов']))
        self.tableWidget.setRowCount(5)
        self.tableWidget.setHorizontalHeaderLabels(self.var_dict['DataFrame']['Названия столбцов'])
        for i, line in enumerate(self.df.sample(5).values.tolist()):
            for j, col in enumerate(line):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(col)))

    def dataframe(self):
        """
        Выводит на вкладку DataFrame всю нужную информацию по DataFrame в целом (
        Названия столбцов, Количество столбцов, Названия и тип столбцов, Количество строк,
        Количество пропущенных клеток, Процент пропущенных клеток)
        """
        self.DataFrameTextEdit.setPlainText('\n' * 20)
        self.DataFrameTextEdit.insertPlainText(
            "".join([f"{k}:\n{v}\n\n" for k, v in self.var_dict['DataFrame'].items()]))
        self.DataFrameTextEdit.setWordWrapMode(QtGui.QTextOption.NoWrap)

    def variables(self):
        """
        Выводит на вкладку Variables всю нужную информацию по каждой переменной в отдельности (
        Тип столбца, Количество уникальных значений, Количество пропущенных значений, Процент пропущенных значений,
        Количество строк - для всех и если число int/float Среднее, Минимальное, 5 перцентиль,
        1 квартиль, Медиана, 3 квартиль, 95 перцентиль, Максимальное, Количество нулей, Процент нулей,
        Стандартное отклонение, Сумма, Наиболее повторяющиеся значения)
        и возможность отображения графиков для выбранного столбца (boxplot, hisplot)
        """
        for name in self.var_dict['DataFrame']['Названия столбцов']:
            self.comboBox.addItem(name)
        self.comboBox.currentIndexChanged.connect(self.change_button_status)

    def change_button_status(self):
        """
        Реализация возможность отображения графиков для выбранного столбца (boxplot, hisplot)
        """
        self.VariablesTextEdit.setPlainText('\n' * 20)
        self.VariablesTextEdit.insertPlainText(
            "".join([f"{k}:\n{v}\n\n" for k, v in self.var_dict['variables'][self.comboBox.currentText()].items()]))
        if self.var_dict['variables'][self.comboBox.currentText()]['Тип столбца'] in ['float64', 'int64']:
            self.pict = Picture(f'folder/{self.comboBox.currentText()}.png')
            self.pict.show()

    def correlation(self):
        """
        Вывод графика корреляции, при нажатии кнопки возможность вывода scatter plot 2-х выбранных графиков
        """
        pixmap = QPixmap('folder/corr.png')
        self.imageHeatmap.resize(pixmap.size())
        self.imageHeatmap.setPixmap(pixmap)
        self.TabWidget.currentChanged.connect(self.tab_widget_changed)
        for name in self.var_dict['DataFrame']['Названия столбцов']:
            if self.var_dict['variables'][name]['Тип столбца'] in ['float64', 'int64']:
                self.comboOx.addItem(name)
                self.comboOy.addItem(name)
        self.ScatterButton.clicked.connect(self.make_scatter)

    def tab_widget_changed(self):
        """
        Действия привязанные на смену вкладки
        """
        if self.TabWidget.tabText(self.TabWidget.currentIndex()) == 'Variables':
            self.change_button_status()
        if self.TabWidget.tabText(self.TabWidget.currentIndex()) == 'Correlations':
            self.make_scatter()

    def make_scatter(self):
        """
        Реализация возможности вывода scatter plot 2-х выбранных графиков
        """
        Ox = self.comboOx.currentText()
        Oy = self.comboOy.currentText()
        if not os.path.exists(f'folder/scatter{Ox}{Oy}.png'):
            fig, (ax1) = plt.subplots(figsize=(10, 10))
            sns.scatterplot(data=self.df, x=Ox, y=Oy, ax=ax1)
            plt.savefig(f'folder/scatter{Ox}{Oy}.png', dpi=75)
            plt.close()
        pixmap2 = QPixmap(f'folder/scatter{Ox}{Oy}.png')
        self.imageScatter.resize(pixmap2.size())
        self.imageScatter.setPixmap(pixmap2)

    def clear_dataframe(self):
        """
        Функции для очистики (удаление дублей, удаление выбросов по каждому столбцу в отдельности)
        и последующего сохранения DataFrame в выбранный формат данных (csv, xlsx, SQL)
        """
        self.dropButton.clicked.connect(self.drop_dulicates)
        self.minSlider.valueChanged.connect(self.slider_changed)
        self.maxSlider.valueChanged.connect(self.slider_changed)
        self.delButton.clicked.connect(self.del_data)
        self.saveButton.clicked.connect(self.save_dataframe)
        self.model = QStandardItemModel()
        self.listview = QListView()
        for i in self.df_copy.select_dtypes(include=['int64', 'float64']).columns:
            self.model.appendRow(QStandardItem(i))
        self.listview.setModel(self.model)
        self.listview.setSelectionMode(QListView.MultiSelection)
        self.verticalLayout.addWidget(self.listview)

    def drop_dulicates(self):
        """
        Удаление дублей в DataFrame
        """
        self.df_copy = self.df_copy.drop_duplicates()

    def slider_changed(self):
        """
        Функция зависящая от изменения 2-х слайдеров, меняет 2 label в зависимости от слайдера
        """
        sender = self.sender()
        value = sender.value()
        if sender.objectName() == 'maxSlider':
            self.maxQuart.setText(str(value))
        else:
            self.minQuart.setText(str(value))

    def del_data(self):
        """
        Удаление выбросов по квартилям, которые зависят от значений, которые выбраны на слайдерах
        Сохранение DataFrame в выбранный формат
        """
        for col in [self.model.data(index) for index in list(self.listview.selectedIndexes())]:
            self.df_copy = self.df_copy[(self.df_copy[col].quantile(
                int(self.minQuart.text()) / 100) < self.df_copy[col]) & (self.df_copy[col] < self.df_copy[col].quantile(
                int(self.maxQuart.text()) / 100))]

    def save_dataframe(self):
        """
        Сохранение DataFrame в выбранный формат (csv, xlsx, SQL)
        """
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить файл", "",
                                                   "CSV (*.csv);;Excel (*.xlsx);;Database (*.db)")
        if file_path:
            file_type = file_path.split(".")[-1]
            if file_type == "csv":
                self.df_copy.to_csv(file_path, index=False)
            elif file_type == "xlsx":
                self.df_copy.to_excel(file_path, index=False)
            elif file_type == "db":
                conn = sqlite3.connect(file_path)
                self.df_copy.to_sql("table_name", conn, if_exists="replace", index=False)
                conn.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.excepthook = except_hook
    sys.exit(app.exec())
