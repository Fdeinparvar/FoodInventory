import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

DB_PATH = r'food.db'
TABLE_NAME = 'basement_freezer'
COLUMNS = ['Item', 'Dateofpurchase', 'Weight', 'Amount']

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def fetch_all(self):
        cur = self.conn.cursor()
        cur.execute(f'SELECT rowid, * FROM {TABLE_NAME}')
        return cur.fetchall()

    def update_row(self, rowid, data):
        cur = self.conn.cursor()
        set_clause = ', '.join([f'{col}=?' for col in COLUMNS])
        cur.execute(f'UPDATE {TABLE_NAME} SET {set_clause} WHERE rowid=?', (*data, rowid))
        self.conn.commit()

    def delete_row(self, rowid):
        cur = self.conn.cursor()
        cur.execute(f'DELETE FROM {TABLE_NAME} WHERE rowid=?', (rowid,))
        self.conn.commit()

    def insert_row(self, data):
        cur = self.conn.cursor()
        placeholders = ', '.join(['?'] * len(COLUMNS))
        cur.execute(f'INSERT INTO {TABLE_NAME} ({', '.join(COLUMNS)}) VALUES ({placeholders})', data)
        self.conn.commit()

    def close(self):
        self.conn.close()

class App(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.title('Basement Freezer Inventory')
        self.db = db_manager
        self.geometry('700x400')
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=COLUMNS, show='headings')
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)
        self.edit_btn = tk.Button(btn_frame, text='Edit Selected', command=self.edit_selected)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.delete_btn = tk.Button(btn_frame, text='Delete Selected', command=self.delete_selected)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self.refresh_btn = tk.Button(btn_frame, text='Refresh', command=self.load_data)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        self.add_btn = tk.Button(btn_frame, text='Add New', command=self.add_new)
        self.add_btn.pack(side=tk.LEFT, padx=5)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.fetch_all()
        for row in rows:
            values = [row[col] for col in COLUMNS]
            self.tree.insert('', tk.END, iid=row['rowid'], values=values)

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('No selection', 'Please select a row to edit.')
            return
        rowid = selected[0]
        old_values = self.tree.item(rowid, 'values')
        new_values = self.open_edit_dialog(old_values, 'Edit Row')
        if new_values is None:
            return
        try:
            self.db.update_row(rowid, new_values)
            self.load_data()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to update row: {e}')

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('No selection', 'Please select a row to delete.')
            return
        rowid = selected[0]
        if messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete the selected row?'):
            try:
                self.db.delete_row(rowid)
                self.load_data()
            except Exception as e:
                messagebox.showerror('Error', f'Failed to delete row: {e}')

    def add_new(self):
        new_values = self.open_edit_dialog([''] * len(COLUMNS), 'Add New Row')
        if new_values is None:
            return
        try:
            self.db.insert_row(new_values)
            self.load_data()
        except Exception as e:
            messagebox.showerror('Error', f'Failed to add row: {e}')

    def open_edit_dialog(self, initial_values, title):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        entries = []
        vars = []
        for i, col in enumerate(COLUMNS):
            tk.Label(dialog, text=col).grid(row=i, column=0, padx=5, pady=5)
            if col == 'amount':
                var = tk.IntVar(value=int(initial_values[i]) if initial_values[i] else 0)
                entry = tk.Spinbox(dialog, from_=0, to=100000, textvariable=var, width=10)
            else:
                var = tk.StringVar(value=initial_values[i])
                entry = tk.Entry(dialog, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            vars.append(var)
        result = []
        def on_ok():
            for i, col in enumerate(COLUMNS):
                val = vars[i].get()
                if col == 'amount':
                    try:
                        val = str(int(val))
                    except ValueError:
                        messagebox.showerror('Error', 'Amount must be an integer.', parent=dialog)
                        return
                result.append(val)
            dialog.destroy()
        def on_cancel():
            dialog.destroy()
        btn_ok = tk.Button(dialog, text='OK', command=on_ok)
        btn_ok.grid(row=len(COLUMNS), column=0, padx=5, pady=10)
        btn_cancel = tk.Button(dialog, text='Cancel', command=on_cancel)
        btn_cancel.grid(row=len(COLUMNS), column=1, padx=5, pady=10)
        dialog.grab_set()
        self.wait_window(dialog)
        if len(result) == len(COLUMNS):
            return result
        else:
            return None

    def on_closing(self):
        self.db.close()
        self.destroy()

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f'Database not found at {DB_PATH}')
    else:
        db = DatabaseManager(DB_PATH)
        app = App(db)
        app.protocol('WM_DELETE_WINDOW', app.on_closing)
        app.mainloop() 