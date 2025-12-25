import tkinter as tk
from tkinter import ttk
from mdbconverter import MdbXmlConverter


# --- ГЛАВНОЕ ПРИЛОЖЕНИЕ С МЕНЮ ---
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Моя программа 2025")
        self.geometry("600x400")
        
        self.current_frame = None
        self._create_menu()
        self._show_welcome_screen()

    def _create_menu(self):
        menubar = tk.Menu(self)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Главная", command=self._show_welcome_screen)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Инструменты
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Открыть конвертер MDB", command=self.open_converter)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        
        self.config(menu=menubar)

    def _clear_frame(self):
        """Удаляет текущий фрейм перед отрисовкой нового"""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def _show_welcome_screen(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self)
        self.current_frame.pack(expand=True, fill='both')
        
        ttk.Label(self.current_frame, text="Добро пожаловать!", font=("Arial", 16)).pack(pady=50)
        ttk.Label(self.current_frame, text="Выберите инструмент в меню сверху").pack()

    def open_converter(self):
        self._clear_frame()
        # Создаем конвертер как дочерний элемент главного окна
        self.current_frame = MdbXmlConverter(self)
        self.current_frame.pack(expand=True, fill='both')

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()