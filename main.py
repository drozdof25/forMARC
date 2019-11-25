import sys
from PyQt5 import QtWidgets
import design
sys.path.append('C:\\MSC.Software\\Marc\\2018.0.0\\mentat2018\\shlib\\win64')
from py_post import *
import random
import numpy as np
from collections import OrderedDict, Counter

class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonbrowse1.clicked.connect(self.browse_file_2d)
        self.buttonbrowse2.clicked.connect(self.browse_file_3d)
        self.pushButton_4.clicked.connect(self.update_graph)
        self.pushButton.clicked.connect(self.clear_graph)
        self.comboBox_8.popupAboutToBeShown.connect(self.update_combobox)
        self.incs = {'2D': [], '3D': []}
        self.path_to_2d_t16 = None
        self.path_to_3d_t16 = None
        self.comboBox_7.addItems(['2D', '3D'])
        self.count_graph = 0

    def browse_file_2d(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл решения', './', 'Post File (*.t16 *.t19)')
        if not file:
            return
        self.lineEdit.setText(file[0])
        self.path_to_2d_t16 = file[0]
        self.change_incs(file[0], '2D')

    def browse_file_3d(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, 'Выберите файл решения', './', 'Post File (*.t16 *.t19)')
        if not file:
            return
        self.lineEdit_2.setText(file[0])
        self.path_to_3d_t16 = file[0]
        self.change_incs(file[0], '3D')

    def change_incs(self, path, solution):
        p = post_open(path)
        incs = p.increments()
        self.incs[solution].clear()
        for i in range(0, incs - 1):
            self.incs[solution].append(str(i))
        self.update_combobox()

    def update_combobox(self):
        self.comboBox_8.clear()
        if str(self.comboBox_7.currentText()) == '2D':
            self.comboBox_8.addItems(self.incs['2D'])
        elif str(self.comboBox_7.currentText()) == '3D':
            self.comboBox_8.addItems(self.incs['3D'])

    def update_graph(self):
        p = post_open(self.path_to_2d_t16)
        p.moveto(1)
        # сгенерировали список элементов
        elements = [dict(id=p.element(i).id, items=p.element(i).items,
                     type=p.element(i).type) for i in range(0, p.elements())]
        # очистили и отсортировали узлы
        for element in elements:
            if element['type'] == 82:
                element['items'].pop()
                element['items'] = list(OrderedDict.fromkeys(element['items']).keys())
        # сгенерировали список границ элементов
        edges = [[element['items'][n], element['items'][n - 1]]
                 for element in elements for n in range(0, len(element['items']))]
        # сортировка узлов и создание словарей
        edges = [tuple(sorted(edge)) for edge in edges]
        # найдём edges которые на границе (т.е в edges должны повторятся лишь единожды)
        repeat = Counter(edges)
        border = [edge for edge in edges if repeat[edge] == 1]
        # найдём координаты узлов на нужном инкременте и в зависимочти от задачи
        X = []
        Y = []
        if str(self.comboBox_7.currentText()) == '2D':
            nodes = [p.node(i).id for i in range(0, p.nodes())]
            p.moveto(int(self.comboBox_8.currentText())+1)
            X = [p.node_displacement(nodes.index(n))[0] + p.node(nodes.index(n)).x
                 for edge in border for n in edge]
            Y = [p.node_displacement(nodes.index(n))[1] + p.node(nodes.index(n)).y
                 for edge in border for n in edge]
        if str(self.comboBox_7.currentText()) == '3D':
            p_3d = post_open(self.path_to_3d_t16)
            p_3d.moveto(0)
            total_repetitions = p_3d.elements()/p.elements()
            nodes_2d = []
            print(total_repetitions)
            for element in elements:
                for node_id in element['items']:
                    if node_id not in nodes_2d:
                        nodes_2d.append(node_id)
            border_3d =[]
            for edge in border:
                edg = []
                for node in edge:
                    nod = node*total_repetitions*2 - total_repetitions + node + len(nodes_2d)
                    edg.append(nod)
                border_3d.append(edg)
            p_3d.moveto(int(self.comboBox_8.currentText()) + 1)
            nodes = [p_3d.node(i).id for i in range(0, p_3d.nodes())]
            X = [p_3d.node_displacement(nodes.index(n))[0] + p_3d.node(nodes.index(n)).x
                 for edge in border_3d for n in edge]
            Y = [abs(p_3d.node_displacement(nodes.index(n))[1] + p_3d.node(nodes.index(n)).y)
                 for edge in border_3d for n in edge]
        if X and Y:
            legend = str(self.lineEdit_3.text())
            main_graph = self.MplWidget.canvas.axes.scatter(X, Y, s=0.5, label=legend)
            max_width_x = max(X)
            max_width_y = Y[X.index(max_width_x)]
            max_height_y = max(Y)
            max_height_x = X[Y.index(max_height_y)]
            self.MplWidget.canvas.axes.axis('equal')
            x1, x2, y1, y2 = self.MplWidget.canvas.axes.axis()
            print(x1, x2, y1, y2)
            self.MplWidget.canvas.axes.grid(True)
            color = main_graph.get_facecolor()
            self.MplWidget.canvas.draw()
            self.MplWidget.canvas.axes.scatter(max_width_x, max_width_y, s=50, marker='X', c=color)
            self.MplWidget.canvas.axes.legend(loc="upper left")
            # self.MplWidget.canvas.axes.legend(labels=[legend2], loc="upper right")
            self.MplWidget.canvas.draw()
            self.MplWidget.canvas.axes.scatter(max_height_x, max_height_y, s=50, marker='*', c=color)
            self.MplWidget.canvas.draw()
            if self.count_graph == 0:
                self.tableWidget.setColumnCount(4)
                self.tableWidget.setHorizontalHeaderLabels(["#", "Подпись", "Широкое место", 'Высота'])
            self.tableWidget.setRowCount(self.count_graph + 1)
            self.tableWidget.setItem(self.count_graph, 0, QtWidgets.QTableWidgetItem(str(self.count_graph)))
            self.tableWidget.setItem(self.count_graph, 1, QtWidgets.QTableWidgetItem(legend))
            width_string_out = 'x= ' + str(round(max_width_x, 5)) + ' y= ' + str(round(max_width_y, 5))
            self.tableWidget.setItem(self.count_graph, 2, QtWidgets.QTableWidgetItem(width_string_out))
            height_string_out = 'x= ' + str(round(max_height_x, 5)) + ' y= ' + str(round(max_height_y, 5))
            self.tableWidget.setItem(self.count_graph, 3, QtWidgets.QTableWidgetItem(height_string_out))
            self.tableWidget.resizeColumnsToContents()
            self.count_graph += 1
    def clear_graph(self):
        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.draw()
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.count_graph = 0
        # for i in range(0, p.elements()):
        #     d = dict(id=p.element(i).id, items=p.element(i).items,
        #              type=p.element(i).type)
        #     elements.append(d)
        #     if elements[i]['type'] == 82:
        #         elements[i]['items'].pop()
        #         elements[i]['items'] = list(OrderedDict.fromkeys(elements[i]['items']).keys())
        #         elements[i]['edges'] = list()
        #         for n in range(0, len(elements[i]['items'])):
        #             node0 = elements[i]['items'][n]
        #             node1 = elements[i]['items'][n - 1]
        #             edge = [node0, node1]
        #             elements[i]['edges'].append(edge)
        #             edges.append(edge)
        # # fs = 500
        # f = random.randint(1, 100)
        # ts = 1 / fs
        # length_of_signal = 100
        # t = np.linspace(0, 1, length_of_signal)
        #
        # cosinus_signal = np.cos(2 * np.pi * f * t)
        # sinus_signal = np.sin(2 * np.pi * f * t)
        #
        # self.MplWidget.canvas.axes.clear()
        # self.MplWidget.canvas.axes.plot(t, cosinus_signal)
        # self.MplWidget.canvas.axes.plot(t, sinus_signal)
        # self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'), loc='upper right')
        # self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
        # self.MplWidget.canvas.draw()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()