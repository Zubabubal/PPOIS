import sqlite3
from datetime import date, datetime
import xml.dom.minidom as minidom
import xml.sax
import os

class Pet:
    def __init__(self, name, birth_date, last_visit_date, vet_name, diagnosis):
        self.name = name
        self.birth_date = birth_date
        self.last_visit_date = last_visit_date
        self.vet_name = vet_name
        self.diagnosis = diagnosis

class DatabaseModel:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("pets.db")
            self.cursor = self.conn.cursor()
            self.init_db()
            self.remove_duplicates()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка инициализации базы данных: {str(e)}")

    def init_db(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birth_date DATE NOT NULL,
                    last_visit_date DATE NOT NULL,
                    vet_name TEXT NOT NULL,
                    diagnosis TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка создания таблицы: {str(e)}")

    def remove_duplicates(self):
        try:
            self.cursor.execute("""
                DELETE FROM pets WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM pets
                    GROUP BY name, birth_date, last_visit_date, vet_name, diagnosis
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка удаления дубликатов: {str(e)}")

    def add_pet(self, pet):
        try:
            birth_date_str = str(pet.birth_date)
            last_visit_date_str = str(pet.last_visit_date)
            self.cursor.execute("""
                SELECT COUNT(*) FROM pets 
                WHERE name = ? AND birth_date = ? AND last_visit_date = ? AND vet_name = ? AND diagnosis = ?
            """, (pet.name, birth_date_str, last_visit_date_str, pet.vet_name, pet.diagnosis))
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("""
                    INSERT INTO pets (name, birth_date, last_visit_date, vet_name, diagnosis)
                    VALUES (?, ?, ?, ?, ?)
                """, (pet.name, birth_date_str, last_visit_date_str, pet.vet_name, pet.diagnosis))
                self.conn.commit()
                return True
            return False
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка добавления записи: {str(e)}")

    def search_pets(self, name=None, birth_date=None, last_visit_date=None, vet_name=None, diagnosis_phrase=None):
        try:
            query = "SELECT * FROM pets WHERE 1=1"
            params = []
            if name and birth_date:
                query += " AND name = ? AND birth_date = ?"
                params.extend([name, str(birth_date)])
            elif last_visit_date and vet_name:
                query += " AND last_visit_date = ? AND vet_name = ?"
                params.extend([str(last_visit_date), vet_name])
            elif diagnosis_phrase:
                query += " AND diagnosis LIKE ?"
                params.append(f"%{diagnosis_phrase}%")
            self.cursor.execute(query, params)
            return [Pet(row[1], date.fromisoformat(row[2]), date.fromisoformat(row[3]), row[4], row[5])
                    for row in self.cursor.fetchall()]
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Ошибка поиска записей: {str(e)}")

    def delete_pets(self, name=None, birth_date=None, last_visit_date=None, vet_name=None, diagnosis_phrase=None):
        try:
            query = "DELETE FROM pets WHERE 1=1"
            params = []
            if name and birth_date:
                query += " AND name = ? AND birth_date = ?"
                params.extend([name, str(birth_date)])
            elif last_visit_date and vet_name:
                query += " AND last_visit_date = ? AND vet_name = ?"
                params.extend([str(last_visit_date), vet_name])
            elif diagnosis_phrase:
                query += " AND diagnosis LIKE ?"
                params.append(f"%{diagnosis_phrase}%")
            self.cursor.execute(query, params)
            deleted = self.cursor.rowcount
            self.conn.commit()
            return deleted
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка удаления записей: {str(e)}")

    def get_pets(self, page, page_size):
        try:
            offset = (page - 1) * page_size
            self.cursor.execute("SELECT * FROM pets LIMIT ? OFFSET ?", (page_size, offset))
            return [Pet(row[1], date.fromisoformat(row[2]), date.fromisoformat(row[3]), row[4], row[5])
                    for row in self.cursor.fetchall()]
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Ошибка получения записей: {str(e)}")

    def get_total_pets(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM pets")
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise RuntimeError(f"Ошибка подсчета записей: {str(e)}")

    def save_to_xml(self):
        try:
            pets = self.get_pets(1, self.get_total_pets())
            doc = minidom.Document()
            root = doc.createElement("pets")
            doc.appendChild(root)
            for pet in pets:
                pet_elem = doc.createElement("pet")
                for field, value in [("name", pet.name), ("birth_date", str(pet.birth_date)),
                                     ("last_visit_date", str(pet.last_visit_date)),
                                     ("vet_name", pet.vet_name), ("diagnosis", pet.diagnosis)]:
                    elem = doc.createElement(field)
                    elem.appendChild(doc.createTextNode(value))
                    pet_elem.appendChild(elem)
                root.appendChild(pet_elem)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"pets_{timestamp}.xml"
            with open(filename, "w", encoding="utf-8") as f:
                doc.writexml(f, indent="  ", addindent="  ", newl="\n")
            return filename
        except (IOError, Exception) as e:
            raise RuntimeError(f"Ошибка сохранения в XML: {str(e)}")

class PetSAXHandler(xml.sax.ContentHandler):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.current_tag = None
        self.pet_data = {}

    def startElement(self, name, attrs):
        self.current_tag = name

    def characters(self, content):
        if self.current_tag in ["name", "birth_date", "last_visit_date", "vet_name", "diagnosis"]:
            self.pet_data[self.current_tag] = content.strip()

    def endElement(self, name):
        if name == "pet":
            try:
                pet = Pet(
                    self.pet_data["name"],
                    date.fromisoformat(self.pet_data["birth_date"]),
                    date.fromisoformat(self.pet_data["last_visit_date"]),
                    self.pet_data["vet_name"],
                    self.pet_data["diagnosis"]
                )
                self.model.add_pet(pet)
            except (ValueError, KeyError) as e:
                print(f"Ошибка обработки записи из XML: {str(e)}")
            self.pet_data = {}
        self.current_tag = None

def load_from_xml(model, filename):
    try:
        parser = xml.sax.make_parser()
        handler = PetSAXHandler(model)
        parser.setContentHandler(handler)
        parser.parse(filename)
    except (xml.sax.SAXParseException, IOError) as e:
        raise RuntimeError(f"Ошибка загрузки XML: {str(e)}")