import polars as pl
import polars_access_mdbtools as pl_access
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import re

# --- КЛАСС КОНВЕРТЕРА (ТЕПЕРЬ ЭТО ФРЕЙМ) ---
class MdbXmlConverter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Значение по умолчанию в виде строки
        default_tables = 'FSMedUsl, FSMUslugi, FSMUZamUsl, LPUUrovMP, FR_MetodHMP, Ref_Otdel, StrOtdel, ZanDoljn, FSModel'
        self.tables_raw = tk.StringVar(value=default_tables)
        # self.tables = [
        #     'FSMedUsl','FSMUslugi','FSMUZamUsl','LPUUrovMP',
        #     'FR_MetodHMP','Ref_Otdel','StrOtdel','ZanDoljn','FSModel'
        # ]
        self.file_path = tk.StringVar()
        self.status_label = tk.StringVar(value="Готов к работе")
        self._create_widgets()

    def _create_widgets(self):
        # --- Основная часть (Центр) ---
        main_content = ttk.Frame(self)
        main_content.pack(expand=True, fill='both', padx=20, pady=20)

        ttk.Label(main_content, text="Конвертер MDB в XML", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Поле выбора файла
        frm_input = ttk.Frame(main_content)
        frm_input.pack(fill='x', pady=10)
        ttk.Entry(frm_input, textvariable=self.file_path).pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 5))
        ttk.Button(frm_input, text="Обзор", command=self._select_file).pack(side=tk.LEFT)

        # Поле выбора таблиц
        sprav_frame = ttk.Frame(main_content)
        sprav_frame.pack(fill='x', pady=10)
        ttk.Label(sprav_frame, text="Список таблиц для выгрузки (через запятую):").pack(anchor='w')
        # Используем Entry для компактности или ScrolledText, если таблиц очень много
        entry_tables = ttk.Entry(sprav_frame, textvariable=self.tables_raw)
        entry_tables.pack(fill='x', pady=(0, 15))

        # Кнопка запуска
        self.btn_run = ttk.Button(main_content, text="Запустить конвертацию", command=self._start_proc)
        self.btn_run.pack(pady=10, fill='x')

        # --- Нижняя панель (Status Bar) ---
        # Создаем фрейм, который будет "приклеен" к низу окна
        status_bar_frame = ttk.Frame(self, relief="sunken", borderwidth=1)
        status_bar_frame.pack(side=tk.BOTTOM, fill='x')

        # Текстовый статус (слева)
        lbl_status = ttk.Label(status_bar_frame, textvariable=self.status_label, width=30)
        lbl_status.pack(side=tk.LEFT, padx=10, pady=2)

        # Прогрессбар (справа, растягивается)
        self.progress = ttk.Progressbar(status_bar_frame, orient="horizontal", mode="determinate") #, maximum=len(self.tables)
        self.progress.pack(side=tk.RIGHT, fill='x', expand=True, padx=10, pady=2)

    def _select_file(self):
        path = filedialog.askopenfilename(filetypes=(("Access DB", "*.mdb"), ("Все файлы", "*.*")))
        if path: self.file_path.set(path)

    def _worker(self):
        path = self.file_path.get().strip()

        # Превращаем строку из Entry в список таблиц, убирая лишние пробелы
        current_tables = [t.strip() for t in self.tables_raw.get().split(',') if t.strip()]

        if not path or not os.path.exists(path):
            self.after(0, lambda: messagebox.showwarning("Ошибка", "Файл не выбран!"))
            return
        
        if not current_tables:
            self.after(0, lambda: messagebox.showwarning("Ошибка", "Список таблиц пуст!"))
            return

        try:
            self.after(0, lambda: self.progress.config(maximum=len(current_tables)))
            self.after(0, lambda: self.btn_run.config(state=tk.DISABLED))
            directory = 'krv_' + datetime.now().strftime('%d%m%Y_%H%M%S')
            os.makedirs(directory, exist_ok=True)
            
            for idx, table in enumerate(current_tables, 1):
                self.after(0, lambda i=idx, t=table: self._update_ui(i, f"Обработка: {t}"))
                self.mdb_to_xml(path, table, os.path.join(directory, table +'.xml') )

                
            self.after(0, lambda: messagebox.showinfo("Успех", f"Файлы в папке: {directory}"))
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Ошибка", str(err)))
        finally:
            self.after(0, self._reset_ui)

    def _start_proc(self):
        threading.Thread(target=self._worker, daemon=True).start()

    def _update_ui(self, val, text):
        self.progress["value"] = val
        self.status_label.set(text)

    def _reset_ui(self):
        self.btn_run.config(state=tk.NORMAL)
        self.progress["value"] = 0
        self.status_label.set("Готов к работе")

    def mdb_to_xml(self, mdb_file_path, table_name, output_xml_path):
        # print(pl_access.list_table_names(mdb_file_path))
        df: pl.DataFrame = pl_access.read_table(mdb_file_path, table_name)
        root = ET.Element("dataroot")
        for row in df.iter_rows(named=True):
            record = ET.SubElement(root, table_name)
            for col_name, value in row.items():
                if value == None: continue
                # if isinstance(value, str) and "." in value and str(value)[-1:] == '0': value = value.rstrip('0').rstrip('.')
                if isinstance(value, str) and bool(re.fullmatch(r'(\d{1,}\.\d*0)', value)): value = value.rstrip('0').rstrip('.')
                field = ET.SubElement(record, col_name)
                field.text = str(value)
        tree = ET.ElementTree(root)
        ET.indent(tree)
        tree.write(output_xml_path, encoding='unicode', xml_declaration=True)

