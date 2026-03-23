import math
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QMessageBox, QFileDialog
from src.view import AddStudentDialog, SearchDialog

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.action_add.triggered.connect(self.show_add_dialog)
        self.view.action_search.triggered.connect(self.show_search_dialog)
        self.view.action_show_all.triggered.connect(self.show_all_students)
        self.view.action_delete.triggered.connect(self.delete_student)
        self.view.action_load_xml.triggered.connect(self.load_xml)
        self.view.action_save_xml.triggered.connect(self.save_xml)

        self.current_data = []
        self.current_page = 1
        self.rows_per_page = self.view.rows_spinbox.value()

        self.view.btn_first.clicked.connect(self.go_to_first_page)
        self.view.btn_prev.clicked.connect(self.go_to_prev_page)
        self.view.btn_next.clicked.connect(self.go_to_next_page)
        self.view.btn_last.clicked.connect(self.go_to_last_page)

        self.view.rows_spinbox.valueChanged.connect(self.change_rows_per_page)

        self.update_table()

    def update_table(self, records=None):
        if records is None:
            self.current_data = self.model.get_all_records()
        else:
            self.current_data = records

        self.current_page = 1

        self.display_page()

    def display_page(self):
        table_model = QStandardItemModel()
        table_model.setHorizontalHeaderLabels([
            'Имя студента', 'ФИО отца', 'ЗП отца',
            'ФИО матери', 'ЗП матери', 'Братья', 'Сестры'
        ])

        total_records = len(self.current_data)

        if total_records == 0:
            self.view.page_label.setText("0 из 0")
            self.view.table.setModel(table_model)
            self.update_pagination_buttons(0)
            return

        total_pages = math.ceil(total_records / self.rows_per_page)

        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.current_data[start_idx:end_idx]

        for row in page_data:
            items_list = [QStandardItem(str(value)) for value in row]
            table_model.appendRow(items_list)

        self.view.table.setModel(table_model)
        self.view.page_label.setText(f"{self.current_page} из {total_pages}")
        self.update_pagination_buttons(total_pages)

    def update_pagination_buttons(self, total_pages):
        self.view.btn_first.setEnabled(self.current_page > 1)
        self.view.btn_prev.setEnabled(self.current_page > 1)

        self.view.btn_next.setEnabled(self.current_page < total_pages)
        self.view.btn_last.setEnabled(self.current_page < total_pages)

    def go_to_first_page(self):
        self.current_page = 1
        self.display_page()

    def go_to_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page()

    def go_to_next_page(self):
        total_pages = math.ceil(len(self.current_data) / self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.display_page()

    def go_to_last_page(self):
        total_pages = math.ceil(len(self.current_data) / self.rows_per_page)
        self.current_page = total_pages
        self.display_page()

    def change_rows_per_page(self, value):
        self.rows_per_page = value
        self.current_page = 1
        self.display_page()

    def show_add_dialog(self):
        dialog = AddStudentDialog(self.view)

        if dialog.exec():
            data = dialog.get_data()

            self.model.add_record(
                data['student_name'],
                data['father_name'],
                data['father_income'],
                data['mother_name'],
                data['mother_income'],
                data['brothers'],
                data['sisters']
            )

            self.update_table()

    def show_search_dialog(self):
        dialog = SearchDialog(self.view, title="Поиск студентов")

        if dialog.exec():
            data = dialog.get_data()

            if data == "error":
                QMessageBox.warning(self.view, "Ошибка", "В числовые поля введен текст!")
                return

            results = self.model.search_records(**data)

            if not results:
                QMessageBox.information(self.view, "Результат", "По вашему запросу ничего не найдено.")

            self.update_table(records=results)

    def show_all_students(self):
        self.update_table()

    def delete_student(self):
        dialog = SearchDialog(self.view, title="Удаление по параметрам")

        if dialog.exec():
            data = dialog.get_data()

            if data == "error":
                QMessageBox.warning(self.view, "Ошибка", "В числовые поля (зарплата, братья, сестры) введен текст!")
                return

            if all(value is None for value in data.values()):
                QMessageBox.warning(self.view, "Ошибка", "Задайте хотя бы один критерий для удаления!")
                return

            reply = QMessageBox.question(
                self.view, "Подтверждение",
                "Вы уверены, что хотите безвозвратно удалить ВСЕХ студентов, подходящих под эти критерии?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                deleted_count = self.model.delete_records_by_criteria(**data)

                if deleted_count > 0:
                    QMessageBox.information(self.view, "Успех", f"Успешно удалено записей: {deleted_count}")
                    self.update_table()
                else:
                    QMessageBox.information(self.view, "Результат",
                                            "По вашим критериям не найдено ни одного студента для удаления.")

    def save_xml(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self.view,
            "Экспорт в XML",
            "students_data.xml",
            "XML файлы (*.xml);;Все файлы (*)"
        )

        if filepath:
            try:
                self.model.export_to_xml(filepath)
                QMessageBox.information(self.view, "Успех", f"База данных успешно сохранена в файл:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_xml(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self.view,
            "Импорт из XML",
            "",
            "XML файлы (*.xml);;Все файлы (*)"
        )

        if filepath:
            try:
                self.model.import_from_xml(filepath)
                self.update_table()
                QMessageBox.information(self.view, "Успех", f"Данные из файла успешно добавлены в базу!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Не удалось прочитать файл XML:\n{e}")

