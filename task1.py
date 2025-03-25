import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- Database Functions (same as before) ---
def create_connection():
    try:
        conn = sqlite3.connect('contacts.db')
        return conn
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        return None

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone_no TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error creating table: {e}")

def create_contact(conn, name, phone_no):
    sql = ''' INSERT INTO contacts(name,phone_no) VALUES(?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (name, phone_no))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Phone number '{phone_no}' already exists.")
        return None
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error creating contact: {e}")
        return None

def read_contacts(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone_no FROM contacts")
    rows = cur.fetchall()
    return rows

def read_contact_by_id(conn, contact_id):
    cur = conn.cursor()
    cur.execute("SELECT id, name, phone_no FROM contacts WHERE id=?", (contact_id,))
    row = cur.fetchone()
    return row

def update_contact(conn, contact_id, new_phone_no):
    sql = ''' UPDATE contacts SET phone_no = ? WHERE id = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, (new_phone_no, contact_id))
        conn.commit()
        return cur.rowcount
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Phone number '{new_phone_no}' already exists.")
        return 0
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error updating contact: {e}")
        return 0

def delete_contact(conn, contact_id):
    sql = 'DELETE FROM contacts WHERE id=?'
    cur = conn.cursor()
    try:
        cur.execute(sql, (contact_id,))
        conn.commit()
        return cur.rowcount
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Error deleting contact: {e}")
        return 0

# --- GUI Functions ---
class ContactApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")

        self.conn = create_connection()
        if self.conn:
            create_table(self.conn)
            self.create_widgets()
            self.populate_contact_list()
        else:
            messagebox.showerror("Error", "Could not connect to the database. Closing application.")
            self.root.destroy()

    def create_widgets(self):
        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.root, text="Contact Details")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Phone No:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = ttk.Entry(input_frame)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # --- Buttons Frame ---
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(buttons_frame, text="Add Contact", command=self.add_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Update Contact", command=self.update_selected_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Contact", command=self.delete_selected_contact).pack(side=tk.LEFT, padx=5)

        # --- Contact List Frame ---
        list_frame = ttk.LabelFrame(self.root, text="Contact List")
        list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.contact_list = ttk.Treeview(list_frame, columns=("ID", "Name", "Phone"), show="headings", selectmode="browse")
        self.contact_list.heading("ID", text="ID")
        self.contact_list.heading("Name", text="Name")
        self.contact_list.heading("Phone", text="Phone No")
        self.contact_list.column("ID", width=50)
        self.contact_list.column("Name", width=150)
        self.contact_list.column("Phone", width=100)
        self.contact_list.pack(fill=tk.BOTH, expand=True)
        self.contact_list.bind("<ButtonRelease-1>", self.populate_entry_fields)

        # --- Configure Grid Layout ---
        self.root.grid_columnconfigure(0, weight=1)

    def populate_contact_list(self):
        self.contact_list.delete(*self.contact_list.get_children())
        contacts = read_contacts(self.conn)
        for contact in contacts:
            self.contact_list.insert("", tk.END, values=contact)

    def populate_entry_fields(self, event):
        selected_item = self.contact_list.selection()
        if selected_item:
            contact_id = self.contact_list.item(selected_item)['values'][0]
            contact = read_contact_by_id(self.conn, contact_id)
            if contact:
                self.name_entry.delete(0, tk.END)
                self.phone_entry.delete(0, tk.END)
                self.name_entry.insert(0, contact[1])
                self.phone_entry.insert(0, contact[2])
            else:
                self.clear_entry_fields()

    def clear_entry_fields(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)

    def add_contact(self):
        name = self.name_entry.get()
        phone_no = self.phone_entry.get()

        if name and phone_no:
            if create_contact(self.conn, name, phone_no):
                messagebox.showinfo("Success", "Contact added successfully.")
                self.populate_contact_list()
                self.clear_entry_fields()
            else:
                # Error message already shown in create_contact
                pass
        else:
            messagebox.showerror("Error", "Name and Phone Number are required.")

    def update_selected_contact(self):
        selected_item = self.contact_list.selection()
        if selected_item:
            contact_id = self.contact_list.item(selected_item)['values'][0]
            name = self.name_entry.get()
            phone_no = self.phone_entry.get()

            if name and phone_no:
                if update_contact(self.conn, contact_id, phone_no):
                    messagebox.showinfo("Success", "Contact updated successfully.")
                    self.populate_contact_list()
                    self.clear_entry_fields()
                else:
                    # Error message already shown in update_contact
                    pass
            else:
                messagebox.showerror("Error", "Name and Phone Number are required.")
        else:
            messagebox.showinfo("Information", "Please select a contact to update.")

    def delete_selected_contact(self):
        selected_item = self.contact_list.selection()
        if selected_item:
            contact_id = self.contact_list.item(selected_item)['values'][0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
                if delete_contact(self.conn, contact_id):
                    messagebox.showinfo("Success", "Contact deleted successfully.")
                    self.populate_contact_list()
                    self.clear_entry_fields()
                else:
                    messagebox.showerror("Error", "Failed to delete contact.")
        else:
            messagebox.showinfo("Information", "Please select a contact to delete.")

def main():
    root = tk.Tk()
    app = ContactApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()