import tkinter as tk
from tkinter import filedialog, messagebox
from model import DatabaseModel, Pet, load_from_xml
from view import MainView, AddDialog, SearchDialog, DeleteDialog

class Controller:
    def __init__(self):
        self.model = DatabaseModel()
        self.root = tk.Tk()
        self.view = MainView(self.root, self)

    def run(self):
        try:
            self.update_view()
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при запуске приложения: {str(e)}")

    def update_view(self):
        try:
            page = self.view.current_page.get()
            page_size = self.view.page_size.get()
            if page_size <= 0:
                page_size = 10
                self.view.page_size.set(page_size)
            pets = self.model.get_pets(page, page_size)
            total_records = self.model.get_total_pets()
            total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
            self.view.update_table(pets, total_pages, total_records)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить таблицу: {str(e)}")

    def update_tree_view(self):
        try:
            pets = self.model.get_pets(1, self.model.get_total_pets())
            self.view.update_tree(pets)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить древовидный вид: {str(e)}")

    def refresh(self):
        try:
            if self.view.table.winfo_ismapped():
                self.update_view()
            elif self.view.tree and self.view.tree.winfo_ismapped():
                self.update_tree_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные: {str(e)}")

    def add_pet(self, name, birth_date, last_visit_date, vet_name, diagnosis):
        try:
            pet = Pet(name, birth_date, last_visit_date, vet_name, diagnosis)
            if self.model.add_pet(pet):
                messagebox.showinfo("Успех", "Питомец успешно добавлен")
            else:
                messagebox.showinfo("Информация", "Запись не добавлена, так как она уже существует")
            self.update_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить питомца: {str(e)}")

    def show_add_dialog(self):
        AddDialog(self.root, self)

    def search_pets(self, name=None, birth_date=None, last_visit_date=None, vet_name=None, diagnosis_phrase=None):
        try:
            return self.model.search_pets(name, birth_date, last_visit_date, vet_name, diagnosis_phrase)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {str(e)}")
            return []

    def show_search_dialog(self):
        SearchDialog(self.root, self)

    def delete_pets(self, name=None, birth_date=None, last_visit_date=None, vet_name=None, diagnosis_phrase=None):
        try:
            deleted = self.model.delete_pets(name, birth_date, last_visit_date, vet_name, diagnosis_phrase)
            self.model.remove_duplicates()
            self.update_view()
            messagebox.showinfo("Результат", f"Удалено {deleted} записей")
            return deleted
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить записи: {str(e)}")
            return 0

    def show_delete_dialog(self):
        DeleteDialog(self.root, self)

    def save_to_xml(self):
        try:
            filename = self.model.save_to_xml()
            messagebox.showinfo("Успех", f"Данные сохранены в файл {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить XML: {str(e)}")

    def load_from_xml(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
            if filename:
                load_from_xml(self.model, filename)
                self.model.remove_duplicates()
                self.update_view()
                messagebox.showinfo("Успех", "Данные успешно загружены из XML")
            else:
                messagebox.showinfo("Информация", "Выбор файла отменен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить XML: {str(e)}")

    def change_page(self, page):
        try:
            page_size = self.view.page_size.get()
            if page_size <= 0:
                page_size = 10
                self.view.page_size.set(page_size)
            total_records = self.model.get_total_pets()
            total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
            if 1 <= page <= total_pages:
                self.view.current_page.set(page)
                self.update_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сменить страницу: {str(e)}")

    def change_page_last(self):
        try:
            page_size = self.view.page_size.get()
            if page_size <= 0:
                page_size = 10
                self.view.page_size.set(page_size)
            total_records = self.model.get_total_pets()
            total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
            self.view.current_page.set(total_pages)
            self.update_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось перейти на последнюю страницу: {str(e)}")