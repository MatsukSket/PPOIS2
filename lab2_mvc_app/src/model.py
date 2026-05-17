import sqlite3
import xml.dom.minidom as minidom
import xml.sax

class DatabaseModel:
    def __init__(self, db_name='students.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_name TEXT, father_name TEXT, father_income REAL,
                mother_name TEXT, mother_income REAL, brothers INTEGER, sisters INTEGER
            )
        ''')
        self.conn.commit()


    def add_record(self, student_name, father_name, father_income, mother_name, mother_income, brothers, sisters):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO students (student_name, father_name, father_income, mother_name, mother_income, brothers, sisters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student_name, father_name, father_income, mother_name, mother_income, brothers, sisters))
        self.conn.commit()

    def get_all_records(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM students')
        return cursor.fetchall()

    def search_records(self, student_name=None,
                       father_name=None,
                       min_father_income=None, max_father_income=None,
                       mother_name=None,
                       min_mother_income=None, max_mother_income=None,
                       min_brothers=None, max_brothers=None,
                       min_sisters=None, max_sisters=None):

        conditions = []
        values = []

        # имя студента
        if student_name:
            conditions.append("student_name LIKE ?")
            values.append(f"%{student_name}%")

        # имя отца
        if father_name:
            conditions.append("father_name LIKE ?")
            values.append(f"%{father_name}%")

        # заработок отца
        if min_father_income is not None:
            conditions.append("father_income >= ?")
            values.append(min_father_income)
        if max_father_income is not None:
            conditions.append("father_income <= ?")
            values.append(max_father_income)

        # имя матери
        if mother_name:
            conditions.append("mother_name LIKE ?")
            values.append(f"%{mother_name}%")

        # заработок матери
        if min_mother_income is not None:
            conditions.append("mother_income >= ?")
            values.append(min_mother_income)
        if max_mother_income is not None:
            conditions.append("mother_income <= ?")
            values.append(max_mother_income)

        # количество братьев
        if min_brothers is not None:
            conditions.append("brothers >= ?")
            values.append(min_brothers)
        if max_brothers is not None:
            conditions.append("brothers <= ?")
            values.append(max_brothers)

        # количество сестер
        if min_sisters is not None:
            conditions.append("sisters >= ?")
            values.append(min_sisters)
        if max_sisters is not None:
            conditions.append("sisters <= ?")
            values.append(max_sisters)

        # итоговый запрос
        query = "SELECT * FROM students"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor = self.conn.cursor()
        cursor.execute(query, values)
        return cursor.fetchall()

    def delete_records_by_criteria(self, student_name=None, father_name=None,
                                   min_father_income=None, max_father_income=None,
                                   mother_name=None, min_mother_income=None, max_mother_income=None,
                                   min_brothers=None, max_brothers=None,
                                   min_sisters=None, max_sisters=None):
        conditions = []
        values = []

        if student_name:
            conditions.append("student_name LIKE ?")
            values.append(f"%{student_name}%")
        if father_name:
            conditions.append("father_name LIKE ?")
            values.append(f"%{father_name}%")
        if min_father_income is not None:
            conditions.append("father_income >= ?")
            values.append(min_father_income)
        if max_father_income is not None:
            conditions.append("father_income <= ?")
            values.append(max_father_income)
        if mother_name:
            conditions.append("mother_name LIKE ?")
            values.append(f"%{mother_name}%")
        if min_mother_income is not None:
            conditions.append("mother_income >= ?")
            values.append(min_mother_income)
        if max_mother_income is not None:
            conditions.append("mother_income <= ?")
            values.append(max_mother_income)
        if min_brothers is not None:
            conditions.append("brothers >= ?")
            values.append(min_brothers)
        if max_brothers is not None:
            conditions.append("brothers <= ?")
            values.append(max_brothers)
        if min_sisters is not None:
            conditions.append("sisters >= ?")
            values.append(min_sisters)
        if max_sisters is not None:
            conditions.append("sisters <= ?")
            values.append(max_sisters)

        if not conditions:
            return 0

        query = "DELETE FROM students WHERE " + " AND ".join(conditions)
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()

        return cursor.rowcount

    def export_to_xml(self, filepath):
        records = self.get_all_records()

        doc = minidom.Document()
        root = doc.createElement('students_data')
        doc.appendChild(root)

        fields = ['student_name', 'father_name', 'father_income',
                  'mother_name', 'mother_income', 'brothers', 'sisters']

        for row in records:
            student_elem = doc.createElement('student')

            for i in range(0, len(fields)):
                field_name = fields[i]
                field_value = str(row[i])

                elem = doc.createElement(field_name)
                text_node = doc.createTextNode(field_value)
                elem.appendChild(text_node)

                student_elem.appendChild(elem)

            root.appendChild(student_elem)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="  "))

    def import_from_xml(self, filepath):
        handler = StudentXMLHandler(self)
        xml.sax.parse(filepath, handler)


class StudentXMLHandler(xml.sax.ContentHandler):
    def __init__(self, db_model):
        self.db = db_model
        self.current_tag = ""

        self.student_name = ""
        self.father_name = ""
        self.father_income = 0.0
        self.mother_name = ""
        self.mother_income = 0.0
        self.brothers = 0
        self.sisters = 0

    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == "student_name":
            self.student_name = ""
        elif tag == "father_name":
            self.father_name = ""
        elif tag == "mother_name":
            self.mother_name = ""

    def characters(self, content):
        if self.current_tag == "student_name":
            self.student_name += content
        elif self.current_tag == "father_name":
            self.father_name += content
        elif self.current_tag == "father_income":
            self.father_income = float(content)
        elif self.current_tag == "mother_name":
            self.mother_name += content
        elif self.current_tag == "mother_income":
            self.mother_income = float(content)
        elif self.current_tag == "brothers":
            self.brothers = int(content)
        elif self.current_tag == "sisters":
            self.sisters = int(content)

    def endElement(self, tag):
        if tag == "student":
            self.db.add_record(
                self.student_name.strip(),
                self.father_name.strip(),
                self.father_income,
                self.mother_name.strip(),
                self.mother_income,
                self.brothers,
                self.sisters
            )
        self.current_tag = ""