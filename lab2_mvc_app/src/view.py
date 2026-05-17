from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLabel, QSpinBox,
    QLineEdit, QDoubleSpinBox, QDialog,
    QFormLayout,QMessageBox,
    QStackedWidget, QTreeView
)
from PySide6.QtGui import QAction
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Студенты')
        self.resize(900, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.setup_menu()
        self.setup_body()
        self.setup_footer()

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        view_menu = menubar.addMenu('Вид')
        student_menu = menubar.addMenu('Студенты')

        # меню файл
        self.action_load_xml = QAction('Загрузить из XML', self)
        self.action_save_xml = QAction('Сохранить в XML',self)

        file_menu.addAction(self.action_load_xml)
        file_menu.addAction(self.action_save_xml)

        # меню вид
        self.action_view_table = QAction('Таблица', self)
        self.action_view_tree = QAction('Дерево', self)
        view_menu.addAction(self.action_view_table)
        view_menu.addAction(self.action_view_tree)

        # меню студенты
        self.action_add = QAction('Добавить студента', self)
        self.action_search = QAction('Найти', self)
        self.action_show_all = QAction('Показать всех', self)
        self.action_delete = QAction('Удалить', self)

        student_menu.addAction(self.action_add)
        student_menu.addAction(self.action_search)
        student_menu.addAction(self.action_show_all)
        student_menu.addAction(self.action_delete)

        toolbar = self.addToolBar('Основная панель')
        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_search)
        toolbar.addAction(self.action_show_all)
        toolbar.addAction(self.action_delete)

    def setup_body(self):
        self.views_stack = QStackedWidget()

        self.table = QTableView()
        self.tree = QTreeView()

        self.views_stack.addWidget(self.table)
        self.views_stack.addWidget(self.tree)

        self.main_layout.addWidget(self.views_stack)

    def setup_footer(self):
        footer_layout = QHBoxLayout()

        self.btn_first = QPushButton("|<")
        self.btn_prev = QPushButton("<")
        self.page_label = QPushButton("1 из ?")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">|")

        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 100)
        self.rows_spinbox.setValue(10)

        footer_layout.addWidget(self.btn_first)
        footer_layout.addWidget(self.btn_prev)
        footer_layout.addWidget(self.page_label)
        footer_layout.addWidget(self.btn_next)
        footer_layout.addWidget(self.btn_last)
        footer_layout.addWidget(QLabel("Строк на странице: "))
        footer_layout.addWidget(self.rows_spinbox)

        self.main_layout.addLayout(footer_layout)

class AddStudentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавление студента')
        self.resize(400,300)

        self.student_name_input = QLineEdit()

        self.father_name_input = QLineEdit()
        self.father_income_input = QDoubleSpinBox()
        self.father_income_input.setMaximum(10000000)

        self.mother_name_input = QLineEdit()
        self.mother_income_input = QDoubleSpinBox()
        self.mother_income_input.setMaximum(10000000)

        self.brothers_input = QSpinBox()
        self.brothers_input.setMaximum(15)
        self.sisters_input = QSpinBox()
        self.sisters_input.setMaximum(15)

        layout = QFormLayout()
        layout.addRow("Имя студента:", self.student_name_input)
        layout.addRow("ФИО отца:", self.father_name_input)
        layout.addRow("Заработок отца:", self.father_income_input)
        layout.addRow("ФИО матери:", self.mother_name_input)
        layout.addRow("Заработок матери:", self.mother_income_input)
        layout.addRow("Количество братьев:", self.brothers_input)
        layout.addRow("Количество сестер:", self.sisters_input)

        button_layout = QHBoxLayout()
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")

        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)

        self.btn_save.clicked.connect(self.validate_and_accept)
        self.btn_cancel.clicked.connect(self.reject)

        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        return {
            "student_name": self.student_name_input.text(),
            "father_name": self.father_name_input.text(),
            "father_income": self.father_income_input.value(),
            "mother_name": self.mother_name_input.text(),
            "mother_income": self.mother_income_input.value(),
            "brothers": self.brothers_input.value(),
            "sisters": self.sisters_input.value()
        }

    def validate_and_accept(self):
        student = self.student_name_input.text().strip()
        father = self.father_name_input.text().strip()
        mother = self.mother_name_input.text().strip()

        if not student or not father or not mother:
            QMessageBox.warning(self, "Ошибка ввода", "Имена студента и родителей обязательны для заполнения!")
            return

        self.accept()


class SearchDialog(QDialog):
    def __init__(self, parent=None, title="Критерии поиска"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 400)

        layout = QFormLayout()

        # Поля
        self.student_name = QLineEdit()
        self.father_name = QLineEdit()
        self.min_father_inc = QLineEdit()
        self.max_father_inc = QLineEdit()
        self.mother_name = QLineEdit()
        self.min_mother_inc = QLineEdit()
        self.max_mother_inc = QLineEdit()
        self.min_brothers = QLineEdit()
        self.max_brothers = QLineEdit()
        self.min_sisters = QLineEdit()
        self.max_sisters = QLineEdit()

        # Макет
        layout.addRow("Имя студента:", self.student_name)
        layout.addRow("ФИО отца:", self.father_name)
        layout.addRow("Мин. заработок отца:", self.min_father_inc)
        layout.addRow("Макс. заработок отца:", self.max_father_inc)
        layout.addRow("ФИО матери:", self.mother_name)
        layout.addRow("Мин. заработок матери:", self.min_mother_inc)
        layout.addRow("Макс. заработок матери:", self.max_mother_inc)
        layout.addRow("Мин. кол-во братьев:", self.min_brothers)
        layout.addRow("Макс. кол-во братьев:", self.max_brothers)
        layout.addRow("Мин. кол-во сестер:", self.min_sisters)
        layout.addRow("Макс. кол-во сестер:", self.max_sisters)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Применить")
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        def parse_float(val):
            return float(val) if val.strip() else None

        def parse_int(val):
            return int(val) if val.strip() else None

        try:
            return {
                "student_name": self.student_name.text().strip() or None,
                "father_name": self.father_name.text().strip() or None,
                "min_father_income": parse_float(self.min_father_inc.text()),
                "max_father_income": parse_float(self.max_father_inc.text()),
                "mother_name": self.mother_name.text().strip() or None,
                "min_mother_income": parse_float(self.min_mother_inc.text()),
                "max_mother_income": parse_float(self.max_mother_inc.text()),
                "min_brothers": parse_int(self.min_brothers.text()),
                "max_brothers": parse_int(self.max_brothers.text()),
                "min_sisters": parse_int(self.min_sisters.text()),
                "max_sisters": parse_int(self.max_sisters.text())
            }
        except ValueError:
            return "error"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())