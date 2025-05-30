import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class MainView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Система управления данными питомцев")
        self.page_size = tk.IntVar(value=10)
        self.current_page = tk.IntVar(value=1)

        # Меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить в XML", command=self.controller.save_to_xml)
        file_menu.add_command(label="Загрузить из XML", command=self.controller.load_from_xml)
        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Действия", menu=action_menu)
        action_menu.add_command(label="Добавить питомца", command=self.controller.show_add_dialog)
        action_menu.add_command(label="Поиск питомцев", command=self.controller.show_search_dialog)
        action_menu.add_command(label="Удалить питомцев", command=self.controller.show_delete_dialog)
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Табличный вид", command=self.show_table_view)
        view_menu.add_command(label="Древовидный вид", command=self.show_tree_view)

        # Панель инструментов
        toolbar = ttk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(toolbar, text="Добавить питомца", command=self.controller.show_add_dialog).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Поиск", command=self.controller.show_search_dialog).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Удалить", command=self.controller.show_delete_dialog).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Сохранить XML", command=self.controller.save_to_xml).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Загрузить XML", command=self.controller.load_from_xml).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Обновить", command=self.controller.refresh).pack(side=tk.LEFT)

        # Основная область
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill="both")

        # Таблица
        self.table = ttk.Treeview(self.main_frame, columns=("Имя", "Дата рождения", "Последний визит", "ФИО ветеринара", "Диагноз"), show="headings")
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        self.table.pack(expand=True, fill="both")

        # Пагинация
        pagination_frame = ttk.Frame(root)
        pagination_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(pagination_frame, text="Первая", command=lambda: self.controller.change_page(1)).pack(side=tk.LEFT)
        ttk.Button(pagination_frame, text="Предыдущая", command=lambda: self.controller.change_page(self.current_page.get() - 1)).pack(side=tk.LEFT)
        ttk.Label(pagination_frame, text="Страница:").pack(side=tk.LEFT)
        ttk.Entry(pagination_frame, textvariable=self.current_page, width=5).pack(side=tk.LEFT)
        ttk.Label(pagination_frame, text="/").pack(side=tk.LEFT)
        self.total_pages_label = ttk.Label(pagination_frame, text="0")
        self.total_pages_label.pack(side=tk.LEFT)
        ttk.Button(pagination_frame, text="Следующая", command=lambda: self.controller.change_page(self.current_page.get() + 1)).pack(side=tk.LEFT)
        ttk.Button(pagination_frame, text="Последняя", command=self.controller.change_page_last).pack(side=tk.LEFT)
        ttk.Label(pagination_frame, text="Размер страницы:").pack(side=tk.LEFT)
        ttk.Entry(pagination_frame, textvariable=self.page_size, width=5).pack(side=tk.LEFT)
        self.total_records_label = ttk.Label(pagination_frame, text="Всего: 0")
        self.total_records_label.pack(side=tk.LEFT)

        self.tree = None
        self.table.pack(expand=True, fill="both")

    def show_table_view(self):
        try:
            if self.tree:
                self.tree.pack_forget()
            self.table.pack(expand=True, fill="both")
            self.controller.update_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить табличный вид: {str(e)}")

    def show_tree_view(self):
        try:
            self.table.pack_forget()
            if not self.tree:
                self.tree = ttk.Treeview(self.main_frame)
            self.tree.pack(expand=True, fill="both")
            self.controller.update_tree_view()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить древовидный вид: {str(e)}")

    def update_table(self, pets, total_pages, total_records):
        try:
            self.table.delete(*self.table.get_children())
            for pet in pets:
                self.table.insert("", "end", values=(pet.name, pet.birth_date, pet.last_visit_date, pet.vet_name, pet.diagnosis))
            self.total_pages_label.config(text=str(total_pages))
            self.total_records_label.config(text=f"Всего: {total_records}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить таблицу: {str(e)}")

    def update_tree(self, pets):
        try:
            if self.tree:
                self.tree.delete(*self.tree.get_children())
                for i, pet in enumerate(pets):
                    parent = self.tree.insert("", "end", text=f"Питомец {i+1}")
                    self.tree.insert(parent, "end", text=f"Имя: {pet.name}")
                    self.tree.insert(parent, "end", text=f"Дата рождения: {pet.birth_date}")
                    self.tree.insert(parent, "end", text=f"Последний визит: {pet.last_visit_date}")
                    self.tree.insert(parent, "end", text=f"ФИО ветеринара: {pet.vet_name}")
                    self.tree.insert(parent, "end", text=f"Диагноз: {pet.diagnosis}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить дерево: {str(e)}")

def validate_date(date_str, field_name, min_date=None, max_date=None):
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if min_date and parsed_date < min_date:
            raise ValueError(f"{field_name} не может быть раньше {min_date.strftime('%Y-%m-%d')}")
        if max_date and parsed_date > max_date:
            raise ValueError(f"{field_name} не может быть позже {max_date.strftime('%Y-%m-%d')}")
        return parsed_date
    except ValueError as e:
        if "does not match format" in str(e):
            raise ValueError(f"{field_name} должна быть в формате ГГГГ-ММ-ДД (например, 2020-05-01)")
        raise e

class AddDialog:
    def __init__(self, parent, controller):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить питомца")
        self.controller = controller

        ttk.Label(self.dialog, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.dialog)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=1, column=0, padx=5, pady=5)
        self.birth_date_entry = ttk.Entry(self.dialog)
        self.birth_date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Дата последнего визита (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.last_visit_entry = ttk.Entry(self.dialog)
        self.last_visit_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="ФИО ветеринара:").grid(row=3, column=0, padx=5, pady=5)
        self.vet_entry = ttk.Entry(self.dialog)
        self.vet_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Диагноз:").grid(row=4, column=0, padx=5, pady=5)
        self.diagnosis_entry = ttk.Entry(self.dialog)
        self.diagnosis_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(self.dialog, text="Добавить", command=self.add_pet).grid(row=5, column=0, columnspan=2, pady=10)

    def add_pet(self):
        try:
            name = self.name_entry.get().strip()
            birth_date_str = self.birth_date_entry.get().strip()
            last_visit_date_str = self.last_visit_entry.get().strip()
            vet_name = self.vet_entry.get().strip()
            diagnosis = self.diagnosis_entry.get().strip()

            if not all([name, vet_name, diagnosis]):
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return

            min_birth_date = date(2000, 1, 1)
            max_birth_date = date(2025, 5, 5)
            birth_date = validate_date(birth_date_str, "Дата рождения", min_date=min_birth_date, max_date=max_birth_date)

            last_visit_date = validate_date(last_visit_date_str, "Дата последнего визита", min_date=birth_date, max_date=max_birth_date)

            self.controller.add_pet(name, birth_date, last_visit_date, vet_name, diagnosis)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить питомца: {str(e)}")

class SearchDialog:
    def __init__(self, parent, controller):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Поиск питомцев")
        self.controller = controller

        # Поиск по имени и дате рождения
        ttk.Label(self.dialog, text="Поиск по имени и дате рождения").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Имя:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry1 = ttk.Entry(self.dialog)
        self.name_entry1.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.dialog, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.birth_date_entry1 = ttk.Entry(self.dialog)
        self.birth_date_entry1.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Поиск", command=self.search_by_name).grid(row=3, column=0, columnspan=2, pady=5)

        # Поиск по дате последнего приема и ФИО ветеринара
        ttk.Label(self.dialog, text="Поиск по дате последнего приема и ФИО ветеринара").grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Дата последнего визита (ГГГГ-ММ-ДД):").grid(row=5, column=0, padx=5, pady=5)
        self.last_visit_entry2 = ttk.Entry(self.dialog)
        self.last_visit_entry2.grid(row=5, column=1, padx=5, pady=5)
        ttk.Label(self.dialog, text="ФИО ветеринара:").grid(row=6, column=0, padx=5, pady=5)
        self.vet_name_entry2 = ttk.Entry(self.dialog)
        self.vet_name_entry2.grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Поиск", command=self.search_by_visit_vet).grid(row=7, column=0, columnspan=2, pady=5)

        # Поиск по фразе из диагноза
        ttk.Label(self.dialog, text="Поиск по фразе из диагноза").grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Фраза из диагноза:").grid(row=9, column=0, padx=5, pady=5)
        self.diagnosis_phrase_entry3 = ttk.Entry(self.dialog)
        self.diagnosis_phrase_entry3.grid(row=9, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Поиск", command=self.search_by_diagnosis).grid(row=10, column=0, columnspan=2, pady=5)

        self.result_table = ttk.Treeview(self.dialog, columns=("Имя", "Дата рождения", "Последний визит", "ФИО ветеринара", "Диагноз"), show="headings")
        for col in self.result_table["columns"]:
            self.result_table.heading(col, text=col)
            self.result_table.column(col, width=100)
        self.result_table.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

    def search_by_name(self):
        try:
            name = self.name_entry1.get().strip()
            birth_date_str = self.birth_date_entry1.get().strip()
            if not name or not birth_date_str:
                messagebox.showerror("Ошибка", "Имя и дата рождения обязательны")
                return
            birth_date = validate_date(birth_date_str, "Дата рождения")
            pets = self.controller.search_pets(name=name, birth_date=birth_date)
            self.update_results(pets)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {str(e)}")

    def search_by_visit_vet(self):
        try:
            last_visit_date_str = self.last_visit_entry2.get().strip()
            vet_name = self.vet_name_entry2.get().strip()
            if not last_visit_date_str or not vet_name:
                messagebox.showerror("Ошибка", "Дата последнего визита и ФИО ветеринара обязательны")
                return
            last_visit_date = validate_date(last_visit_date_str, "Дата последнего визита")
            pets = self.controller.search_pets(last_visit_date=last_visit_date, vet_name=vet_name)
            self.update_results(pets)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {str(e)}")

    def search_by_diagnosis(self):
        try:
            diagnosis_phrase = self.diagnosis_phrase_entry3.get().strip()
            if not diagnosis_phrase:
                messagebox.showerror("Ошибка", "Фраза из диагноза обязательна")
                return
            pets = self.controller.search_pets(diagnosis_phrase=diagnosis_phrase)
            self.update_results(pets)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {str(e)}")

    def update_results(self, pets):
        try:
            self.result_table.delete(*self.result_table.get_children())
            for pet in pets:
                self.result_table.insert("", "end", values=(pet.name, pet.birth_date, pet.last_visit_date, pet.vet_name, pet.diagnosis))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отобразить результаты: {str(e)}")

class DeleteDialog:
    def __init__(self, parent, controller):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Удаление питомцев")
        self.controller = controller

        # Удаление по имени и дате рождения
        ttk.Label(self.dialog, text="Удаление по имени и дате рождения").grid(row=0, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Имя:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry1 = ttk.Entry(self.dialog)
        self.name_entry1.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.dialog, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.birth_date_entry1 = ttk.Entry(self.dialog)
        self.birth_date_entry1.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Удалить", command=self.delete_by_name).grid(row=3, column=0, columnspan=2, pady=5)

        # Удаление по дате последнего приема и ФИО ветеринара
        ttk.Label(self.dialog, text="Удаление по дате последнего приема и ФИО ветеринара").grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Дата последнего визита (ГГГГ-ММ-ДД):").grid(row=5, column=0, padx=5, pady=5)
        self.last_visit_entry2 = ttk.Entry(self.dialog)
        self.last_visit_entry2.grid(row=5, column=1, padx=5, pady=5)
        ttk.Label(self.dialog, text="ФИО ветеринара:").grid(row=6, column=0, padx=5, pady=5)
        self.vet_name_entry2 = ttk.Entry(self.dialog)
        self.vet_name_entry2.grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Удалить", command=self.delete_by_visit_vet).grid(row=7, column=0, columnspan=2, pady=5)

        # Удаление по фразе из диагноза
        ttk.Label(self.dialog, text="Удаление по фразе из диагноза").grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Label(self.dialog, text="Фраза из диагноза:").grid(row=9, column=0, padx=5, pady=5)
        self.diagnosis_phrase_entry3 = ttk.Entry(self.dialog)
        self.diagnosis_phrase_entry3.grid(row=9, column=1, padx=5, pady=5)
        ttk.Button(self.dialog, text="Удалить", command=self.delete_by_diagnosis).grid(row=10, column=0, columnspan=2, pady=5)

    def delete_by_name(self):
        try:
            name = self.name_entry1.get().strip()
            birth_date_str = self.birth_date_entry1.get().strip()
            if not name or not birth_date_str:
                messagebox.showerror("Ошибка", "Имя и дата рождения обязательны")
                return
            birth_date = validate_date(birth_date_str, "Дата рождения")
            self.controller.delete_pets(name=name, birth_date=birth_date)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить записи: {str(e)}")

    def delete_by_visit_vet(self):
        try:
            last_visit_date_str = self.last_visit_entry2.get().strip()
            vet_name = self.vet_name_entry2.get().strip()
            if not last_visit_date_str or not vet_name:
                messagebox.showerror("Ошибка", "Дата последнего визита и ФИО ветеринара обязательны")
                return
            last_visit_date = validate_date(last_visit_date_str, "Дата последнего визита")
            self.controller.delete_pets(last_visit_date=last_visit_date, vet_name=vet_name)
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить записи: {str(e)}")

    def delete_by_diagnosis(self):
        try:
            diagnosis_phrase = self.diagnosis_phrase_entry3.get().strip()
            if not diagnosis_phrase:
                messagebox.showerror("Ошибка", "Фраза из диагноза обязательна")
                return
            self.controller.delete_pets(diagnosis_phrase=diagnosis_phrase)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить записи: {str(e)}")