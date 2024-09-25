import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime, timedelta
import webbrowser
import json
import csv
import os

# Database setup
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    line_items TEXT,
                    subtotal REAL,
                    date TEXT,
                    status TEXT DEFAULT 'Unpaid',
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS line_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    unit_price REAL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    billing_address TEXT,
                    contact_name TEXT,
                    phone_number TEXT,
                    email TEXT
                )''') 

conn.commit()

# Function to load line items from database
def load_line_items():
    cursor.execute("SELECT * FROM line_items")
    return cursor.fetchall()

def load_clients():
    cursor.execute("Select * FROM clients")
    return cursor.fetchall()

class ClientDialog(tk.Toplevel):
    def __init__(self, parent, title, client=None):
        super().__init__(parent)
        self.title(title)
        self.client = client
        self.result = None

        # Create and set up variables
        self.name_var = tk.StringVar(value=client[1] if client else "")
        self.billing_address_var = tk.StringVar(value=client[2] if client else "")
        self.contact_name_var = tk.StringVar(value=client[3] if client else "")
        self.phone_number_var = tk.StringVar(value=client[4] if client else "")
        self.email_var = tk.StringVar(value=client[5] if client else "")

        # Create and place widgets
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Billing Address:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.billing_address_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Contact Name:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.contact_name_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self, text="Phone Number:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.phone_number_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self, text="Email:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.email_var, width=30).grid(row=4, column=1, padx=5, pady=5)

        # Add OK and Cancel buttons
        tk.Button(self, text="OK", command=self.on_ok).grid(row=5, column=0, padx=5, pady=5)
        tk.Button(self, text="Cancel", command=self.on_cancel).grid(row=5, column=1, padx=5, pady=5)

        self.grab_set()  # Make the dialog modal
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Handle window close button

    def on_ok(self):
        self.result = (
            self.name_var.get(),
            self.billing_address_var.get(),
            self.contact_name_var.get(),
            self.phone_number_var.get(),
            self.email_var.get()
        )
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

# Main application
class InvoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invoice Generator")
        self.geometry("1000x800")

        # Load preferences
        self.preferences = self.load_preferences()

        # Create menu bar
        self.create_menu_bar()

        self.line_items = load_line_items()
        self.clients = load_clients()

        if not self.line_items:
            self.initialize_default_line_items()
            self.line_items = load_line_items()

        # Create form fields
        self.client_var = tk.StringVar()
        self.qty_vars = [tk.StringVar(value="0") for _ in self.line_items]

        tk.Label(self, text="Client").grid(row=0, column=0)
        self.client_dropdown = ttk.Combobox(self, textvariable=self.client_var)
        self.client_dropdown.grid(row=0, column=1)
        self.update_client_dropdown()

        # Create a frame to contain the canvas and scrollbar
        self.line_items_frame = tk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        self.line_items_frame.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)

        # Create a canvas for line items
        self.line_items_canvas = tk.Canvas(self.line_items_frame)
        self.line_items_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the frame
        self.scrollbar = ttk.Scrollbar(self.line_items_frame, orient="vertical", command=self.line_items_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.line_items_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the line items
        self.canvas_frame = tk.Frame(self.line_items_canvas)
        self.canvas_window = self.line_items_canvas.create_window((0, 0), window=self.canvas_frame, anchor='nw')

        # Bind events to handle scrolling and resizing
        self.canvas_frame.bind("<Configure>", self.on_frame_configure)
        self.line_items_canvas.bind("<Configure>", self.on_canvas_configure)

        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
                    
        # Display line items for quantity entry
        self.display_line_items()

        # Buttons
        self.create_button = tk.Button(self, text="Create Invoice", command=self.create_invoice)
        self.create_button.grid(row=8, column=0, pady=10)

        self.update_button = tk.Button(self, text="Update Invoice", command=self.update_invoice)
        self.update_button.grid(row=8, column=1, pady=10)

        self.delete_button = tk.Button(self, text="Delete Invoice", command=self.delete_invoice)
        self.delete_button.grid(row=8, column=2, pady=10)

        self.delete_button = tk.Button(self, text="Mark as Paid", command=self.mark_as_paid)
        self.delete_button.grid(row=9, column=0, pady=10)

        self.delete_button = tk.Button(self, text="Mark as Unpaid", command=self.mark_as_unpaid)
        self.delete_button.grid(row=9, column=1, pady=10)

        self.print_button = tk.Button(self, text="Print Invoice", command=self.print_invoice)
        self.print_button.grid(row=9, column=2, pady=10)

        self.manage_items_button = tk.Button(self, text="Manage Line Items", command=self.manage_line_items)
        self.manage_items_button.grid(row=10, column=0, pady=10)

        self.manage_clients_button = tk.Button(self, text="Manage Clients", command=self.manage_clients)
        self.manage_clients_button.grid(row=10, column=1, pady=10)

        # Add filter options
        filter_frame = tk.Frame(self)
        filter_frame.grid(row=11, column=0, columnspan=3, pady=10)

        tk.Label(filter_frame, text="Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="All")
        status_options = ["All", "Paid", "Unpaid"]
        status_menu = tk.OptionMenu(filter_frame, self.status_var, *status_options, command=self.apply_filters)
        status_menu.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="From:").pack(side=tk.LEFT)
        self.from_date = tk.Entry(filter_frame, width=10)
        self.from_date.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="To:").pack(side=tk.LEFT)
        self.to_date = tk.Entry(filter_frame, width=10)
        self.to_date.pack(side=tk.LEFT)

        tk.Button(filter_frame, text="Apply Date Filter", command=self.apply_filters).pack(side=tk.LEFT)


        # Invoice list
        self.invoice_list = ttk.Treeview(self, columns=("id", "client_name", "subtotal", "date", "status"), show="headings")
        self.invoice_list.heading("id", text="ID", command=lambda: self.treeview_sort_column("id", False))
        self.invoice_list.heading("client_name", text="Client Name", command=lambda: self.treeview_sort_column("client_name", False))
        self.invoice_list.heading("subtotal", text="Subtotal", command=lambda: self.treeview_sort_column("subtotal", False))
        self.invoice_list.heading("date", text="Date", command=lambda: self.treeview_sort_column("date", False))
        self.invoice_list.heading("status", text="Status", command=lambda: self.treeview_sort_column("status", False))
        self.invoice_list.grid(row=12, column=0, columnspan=3, sticky="nsew")

        # Add a scrollbar to the invoice list
        invoice_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.invoice_list.yview)
        invoice_scrollbar.grid(row=12, column=4, sticky="ns")
        self.invoice_list.configure(yscrollcommand=invoice_scrollbar.set)

        # Configure grid weights to make the treeviews expandable
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(13, weight=1)

        # Add the line items treeview
        self.line_items_tree = ttk.Treeview(self, columns=("item", "quantity", "price", "total"), show="headings")
        self.line_items_tree.heading("item", text="Item")
        self.line_items_tree.heading("quantity", text="Quantity")
        self.line_items_tree.heading("price", text="Unit Price")
        self.line_items_tree.heading("total", text="Total")
        self.line_items_tree.grid(row=13, column=0, columnspan=3, sticky="nsew")

        # Add a scrollbar to the line items treeview
        line_items_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.line_items_tree.yview)
        line_items_scrollbar.grid(row=13, column=4, sticky="ns")
        self.line_items_tree.configure(yscrollcommand=line_items_scrollbar.set)

        # Configure grid weights to make the treeviews expandable
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(12, weight=1)

        # Bind the selection event of the invoice list to update line items
        self.invoice_list.bind("<<TreeviewSelect>>", self.on_invoice_select)

        self.load_invoices()

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Invoices to CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self.open_preferences)

    def export_to_csv(self):
        # Get all invoices from the database
        cursor.execute("""
            SELECT invoices.id, clients.name, invoices.subtotal, invoices.date, invoices.status
            FROM invoices
            JOIN clients ON invoices.client_id = clients.id
        """)
        invoices = cursor.fetchall()

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv")
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                csv_writer.writerow(['Invoice ID', 'Client Name', 'Subtotal', 'Date', 'Status'])
                # Write data
                csv_writer.writerows(invoices)
            tk.messagebox.showinfo("Export Successful", f"Invoices exported to {file_path}")

    def open_preferences(self):
        preferences_window = tk.Toplevel(self)
        preferences_window.title("Preferences")
        preferences_window.geometry("400x400")

        # Existing fields
        tk.Label(preferences_window, text="Company Name:").grid(row=0, column=0, padx=5, pady=5)
        company_name_entry = tk.Entry(preferences_window, width=30)
        company_name_entry.grid(row=0, column=1, padx=5, pady=5)
        company_name_entry.insert(0, self.preferences.get('company_name', ''))

        tk.Label(preferences_window, text="Company Address:").grid(row=1, column=0, padx=5, pady=5)
        company_address_entry = tk.Entry(preferences_window, width=30)
        company_address_entry.grid(row=1, column=1, padx=5, pady=5)
        company_address_entry.insert(0, self.preferences.get('company_address', ''))

        # New fields for city, state/province, and postal code
        tk.Label(preferences_window, text="City:").grid(row=2, column=0, padx=5, pady=5)
        company_city_entry = tk.Entry(preferences_window, width=30)
        company_city_entry.grid(row=2, column=1, padx=5, pady=5)
        company_city_entry.insert(0, self.preferences.get('company_city', ''))

        tk.Label(preferences_window, text="State/Province:").grid(row=3, column=0, padx=5, pady=5)
        company_state_entry = tk.Entry(preferences_window, width=30)
        company_state_entry.grid(row=3, column=1, padx=5, pady=5)
        company_state_entry.insert(0, self.preferences.get('company_state', ''))

        tk.Label(preferences_window, text="Postal Code:").grid(row=4, column=0, padx=5, pady=5)
        company_postal_entry = tk.Entry(preferences_window, width=30)
        company_postal_entry.grid(row=4, column=1, padx=5, pady=5)
        company_postal_entry.insert(0, self.preferences.get('company_postal', ''))

        # GST Number
        tk.Label(preferences_window, text="GST Number:").grid(row=5, column=0, padx=5, pady=5)
        gst_number_entry = tk.Entry(preferences_window, width=30)
        gst_number_entry.grid(row=5, column=1, padx=5, pady=5)
        gst_number_entry.insert(0, self.preferences.get('gst_number', ''))

        # Company Phone
        tk.Label(preferences_window, text="Company Phone:").grid(row=6, column=0, padx=5, pady=5)
        company_phone_entry = tk.Entry(preferences_window, width=30)
        company_phone_entry.grid(row=6, column=1, padx=5, pady=5)
        company_phone_entry.insert(0, self.preferences.get('company_phone', ''))

        # Company Email
        tk.Label(preferences_window, text="Company Email:").grid(row=7, column=0, padx=5, pady=5)
        company_email_entry = tk.Entry(preferences_window, width=30)
        company_email_entry.grid(row=7, column=1, padx=5, pady=5)
        company_email_entry.insert(0, self.preferences.get('company_email', ''))

        # Company Website
        tk.Label(preferences_window, text="Company Website:").grid(row=8, column=0, padx=5, pady=5)
        company_website_entry = tk.Entry(preferences_window, width=30)
        company_website_entry.grid(row=8, column=1, padx=5, pady=5)
        company_website_entry.insert(0, self.preferences.get('company_website', ''))

        def save_preferences():
            self.preferences['company_name'] = company_name_entry.get()
            self.preferences['company_address'] = company_address_entry.get()
            self.preferences['company_city'] = company_city_entry.get()
            self.preferences['company_state'] = company_state_entry.get()
            self.preferences['company_postal'] = company_postal_entry.get()
            self.preferences['gst_number'] = gst_number_entry.get()
            self.preferences['company_phone'] = company_phone_entry.get()
            self.preferences['company_email'] = company_email_entry.get()
            self.preferences['company_website'] = company_website_entry.get()
            self.save_preferences()
            preferences_window.destroy()

        save_button = tk.Button(preferences_window, text="Save", command=save_preferences)
        save_button.grid(row=9, column=0, columnspan=2, pady=10)

    def load_preferences(self):
        if os.path.exists('preferences.json'):
            with open('preferences.json', 'r') as f:
                return json.load(f)
        return {}

    def save_preferences(self):
        with open('preferences.json', 'w') as f:
            json.dump(self.preferences, f)

    def on_frame_configure(self, event):
        self.line_items_canvas.configure(scrollregion=self.line_items_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.line_items_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def treeview_sort_column(self, col, reverse):
        l = [(self.invoice_list.set(k, col), k) for k in self.invoice_list.get_children('')]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.invoice_list.move(k, '', index)

        # Reverse sort next time
        self.invoice_list.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))

    def load_invoices(self):
        for row in self.invoice_list.get_children():
            self.invoice_list.delete(row)
        
        status_filter = self.status_var.get()
        from_date = self.from_date.get()
        to_date = self.to_date.get()

        query = """
            SELECT invoices.id, clients.name, invoices.subtotal, invoices.date, invoices.status
            FROM invoices
            JOIN clients ON invoices.client_id = clients.id
            WHERE 1=1
        """
        params = []

        if status_filter != "All":
            query += " AND invoices.status = ?"
            params.append(status_filter.lower())

        if from_date:
            query += " AND invoices.date >= ?"
            params.append(from_date)

        if to_date:
            query += " AND invoices.date <= ?"
            params.append(to_date)

        cursor.execute(query, params)
        for row in cursor.fetchall():
            self.invoice_list.insert("", tk.END, values=row)

    def apply_filters(self, *args):
        self.load_invoices()

    def on_invoice_select(self, event):
        selected_items = self.invoice_list.selection()
        if selected_items:
            invoice_id = self.invoice_list.item(selected_items[0])['values'][0]
            self.load_line_items(invoice_id)

    def load_line_items(self, invoice_id):
        # Clear existing items
        for item in self.line_items_tree.get_children():
            self.line_items_tree.delete(item)

        # Fetch line items for the selected invoice
        cursor.execute("SELECT line_items FROM invoices WHERE id=?", (invoice_id,))
        result = cursor.fetchone()
        if result:
            line_items_str = result[0]
            lines = line_items_str.strip().split('\n')
            for line in lines:
                if ':' in line:
                    item, details = line.split(':', 1)
                    details = details.strip()
                    if '@' in details and '=' in details:
                        quantity, rest = details.split('@')
                        price, total = rest.split('=')
                        quantity = quantity.strip()
                        price = price.strip().replace('$', '')
                        total = total.strip().replace('$', '')
                        self.line_items_tree.insert("", "end", values=(item.strip(), quantity, price, total))


    def manage_clients(self):
        manage_window = tk.Toplevel(self)
        manage_window.title("Manage Clients")
        manage_window.geometry("600x400")

        # Create a frame for the clients list
        list_frame = tk.Frame(manage_window)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a listbox for clients
        self.clients_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.clients_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.clients_listbox.yview)

        # Populate the listbox
        for client in self.clients:
            self.clients_listbox.insert(tk.END, f"{client[1]} - {client[3]}")

        # Create buttons for managing clients
        add_button = tk.Button(manage_window, text="Add Client", command=self.add_client)
        add_button.pack(pady=5)

        edit_button = tk.Button(manage_window, text="Edit Client", command=self.edit_client)
        edit_button.pack(pady=5)

        delete_button = tk.Button(manage_window, text="Delete Client", command=self.delete_client)
        delete_button.pack(pady=5)

    def add_client(self):
        dialog = ClientDialog(self, "Add Client")
        self.wait_window(dialog)
        if dialog.result:
            name, billing_address, contact_name, phone_number, email = dialog.result
            cursor.execute("""
                INSERT INTO clients (name, billing_address, contact_name, phone_number, email)
                VALUES (?, ?, ?, ?, ?)
            """, (name, billing_address, contact_name, phone_number, email))
            conn.commit()
            self.refresh_clients()
            self.clients_listbox.insert(tk.END, f"{name} - {contact_name}")

    def edit_client(self):
        selected = self.clients_listbox.curselection()
        if selected:
            index = selected[0]
            client = self.clients[index]
            dialog = ClientDialog(self, "Edit Client", client)
            self.wait_window(dialog)
            if dialog.result:
                name, billing_address, contact_name, phone_number, email = dialog.result
                cursor.execute("""
                    UPDATE clients 
                    SET name=?, billing_address=?, contact_name=?, phone_number=?, email=?
                    WHERE id=?
                """, (name, billing_address, contact_name, phone_number, email, client[0]))
                conn.commit()
                self.refresh_clients()
                self.clients_listbox.delete(index)
                self.clients_listbox.insert(index, f"{name} - {contact_name}")

    def delete_client(self):
        selected = self.clients_listbox.curselection()
        if selected:
            index = selected[0]
            client = self.clients[index]
            
            # Check if there are any invoices for this client
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE client_id=?", (client[0],))
            invoice_count = cursor.fetchone()[0]
            
            if invoice_count > 0:
                messagebox.showerror("Cannot Delete", f"Cannot delete {client[1]}. There are {invoice_count} invoice(s) associated with this client.")
            else:
                if messagebox.askyesno("Delete Client", f"Are you sure you want to delete {client[1]}?"):
                    cursor.execute("DELETE FROM clients WHERE id=?", (client[0],))
                    conn.commit()
                    self.refresh_clients()
                    self.clients_listbox.delete(index)
                    messagebox.showinfo("Success", f"{client[1]} has been deleted.")

    def refresh_clients(self):
        self.clients = load_clients()
        self.update_client_dropdown()


    def manage_line_items(self):
        manage_window = tk.Toplevel(self)
        manage_window.title("Manage Line Items")
        manage_window.geometry("500x400")

        # Create a frame for the line items list
        list_frame = tk.Frame(manage_window)
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a listbox for line items
        self.items_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.items_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.items_listbox.yview)

        # Populate the listbox
        for item in self.line_items:
            self.items_listbox.insert(tk.END, f"{item[1]} - ${item[2]:.2f}")

        # Create buttons for managing line items
        add_button = tk.Button(manage_window, text="Add Item", command=self.add_line_item)
        add_button.pack(pady=5)

        edit_button = tk.Button(manage_window, text="Edit Item", command=self.edit_line_item)
        edit_button.pack(pady=5)

        delete_button = tk.Button(manage_window, text="Delete Item", command=self.delete_line_item)
        delete_button.pack(pady=5)

    def add_line_item(self):
        name = simpledialog.askstring("Add Line Item", "Enter item name:")
        if name:
            price = simpledialog.askfloat("Add Line Item", f"Enter unit price for {name}:")
            if price is not None:
                cursor.execute("INSERT INTO line_items (name, unit_price) VALUES (?, ?)", (name, price))
                conn.commit()
                self.refresh_line_items()
                self.items_listbox.insert(tk.END, f"{name} - ${price:.2f}")

    def edit_line_item(self):
        selected = self.items_listbox.curselection()
        if selected:
            index = selected[0]
            item = self.line_items[index]
            name = simpledialog.askstring("Edit Line Item", "Enter new item name:", initialvalue=item[1])
            if name:
                price = simpledialog.askfloat("Edit Line Item", f"Enter new unit price for {name}:", initialvalue=item[2])
                if price is not None:
                    cursor.execute("UPDATE line_items SET name=?, unit_price=? WHERE id=?", (name, price, item[0]))
                    conn.commit()
                    self.refresh_line_items()
                    self.items_listbox.delete(index)
                    self.items_listbox.insert(index, f"{name} - ${price:.2f}")

    def delete_line_item(self):
        selected = self.items_listbox.curselection()
        if selected:
            index = selected[0]
            item = self.line_items[index]
            if messagebox.askyesno("Delete Line Item", f"Are you sure you want to delete {item[1]}?"):
                cursor.execute("DELETE FROM line_items WHERE id=?", (item[0],))
                conn.commit()
                self.refresh_line_items()
                self.items_listbox.delete(index)

    def initialize_default_line_items(self):
        default_items = [
            ("38 Meter pump rental hourly (3 hr minimum)", 230),
            ("Meters of pumped concrete", 5),
            ("Offsite wash out fee", 150),
            ("Travel time hourly", 230),
            ("Slurry", 40),
            ("Ferry fees incurred", 113.05),
        ]
        cursor.executemany("INSERT INTO line_items (name, unit_price) VALUES (?, ?)", default_items)
        conn.commit()
    
    def display_line_items(self):
        # Clear existing widgets in the frame
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Configure the columns in the canvas_frame
        self.canvas_frame.columnconfigure(0, weight=3)  # Item name column
        self.canvas_frame.columnconfigure(1, weight=2)  # Unit price column
        self.canvas_frame.columnconfigure(2, weight=1)  # Quantity entry column

        # Re-create quantity entry fields
        self.qty_vars = [tk.StringVar(value="0") for _ in self.line_items]

        # Add headers
        tk.Label(self.canvas_frame, text="Item", font=('Arial', 10, 'bold'), anchor='w').grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        tk.Label(self.canvas_frame, text="Unit Price", font=('Arial', 10, 'bold'), anchor='w').grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        tk.Label(self.canvas_frame, text="Quantity", font=('Arial', 10, 'bold'), anchor='w').grid(row=0, column=2, sticky='ew', padx=5, pady=5)

        for i, item in enumerate(self.line_items):
            # Item name label
            name_label = tk.Label(self.canvas_frame, text=f"{item[1]}", anchor='w')
            name_label.grid(row=i + 1, column=0, sticky='ew', padx=5, pady=2)

            # Unit price label
            price_label = tk.Label(self.canvas_frame, text=f"${item[2]:.2f}", anchor='w')
            price_label.grid(row=i + 1, column=1, sticky='ew', padx=5, pady=2)

            # Quantity entry
            qty_entry = tk.Entry(self.canvas_frame, textvariable=self.qty_vars[i], width=10, justify='left')
            qty_entry.grid(row=i + 1, column=2, sticky='w', padx=5, pady=2)

        # Update the canvas scroll region
        self.canvas_frame.update_idletasks()
        self.line_items_canvas.configure(scrollregion=self.line_items_canvas.bbox("all"))

    def refresh_line_items(self):
        self.line_items = load_line_items()
        self.display_line_items()

    def update_client_dropdown(self):
        self.client_dropdown['values'] = [client[1] for client in self.clients]


    # Create a new invoice
    def create_invoice(self):
        client_name = self.client_var.get()
        date = datetime.now().strftime("%Y-%m-%d")
        line_items_str, subtotal = self.calculate_subtotal()

        if client_name and line_items_str and subtotal > 0:
            client_id = next((client[0] for client in self.clients if client[1] == client_name), None)
            if client_id is None:
                messagebox.showwarning("Error", "Please select a valid client.")
                return

            cursor.execute("""
                INSERT INTO invoices (client_id, line_items, subtotal, date, status) 
                VALUES (?, ?, ?, ?, 'unpaid')
            """, (client_id, line_items_str, subtotal, date))
            conn.commit()
            self.load_invoices()
            self.clear_fields()
            messagebox.showinfo("Success", "Invoice created successfully!")
        else:
            messagebox.showwarning("Error", "Please fill in all fields.")

    # Calculate subtotal based on line items
    def calculate_subtotal(self):
        line_items_str = ""
        subtotal = 0.0

        for i, item in enumerate(self.line_items):
            qty = float(self.qty_vars[i].get())
            total = qty * item[2]
            subtotal += total
            line_items_str += f"{item[1]}: {qty} @ ${item[2]} = ${total:.2f}\n"

        return line_items_str, subtotal

    # Update an existing invoice
    def update_invoice(self):
        selected_item = self.invoice_list.selection()
        if selected_item:
            invoice_id = self.invoice_list.item(selected_item)['values'][0]
            client_name = self.client_var.get()
            line_items_str, subtotal = self.calculate_subtotal()

            if client_name and line_items_str and subtotal > 0:
                client_id = next((client[0] for client in self.clients if client[1] == client_name), None)
                if client_id is None:
                    messagebox.showwarning("Error", "Please select a valid client.")
                    return

                cursor.execute("""
                    UPDATE invoices 
                    SET client_id=?, line_items=?, subtotal=? 
                    WHERE id=?
                """, (client_id, line_items_str, subtotal, invoice_id))
                conn.commit()
                self.load_invoices()
                self.clear_fields()
                messagebox.showinfo("Success", "Invoice updated successfully!")
            else:
                messagebox.showwarning("Error", "Please fill in all fields.")
        else:
            messagebox.showwarning("Error", "Please select an invoice to update.")
    
    # Mark an invoice as unpaid
    def mark_as_unpaid(self):
        selected_item = self.invoice_list.selection()
        if selected_item:
            invoice_id = self.invoice_list.item(selected_item)['values'][0]
            cursor.execute("UPDATE invoices SET status='unpaid' WHERE id=?", (invoice_id,))
            conn.commit()
            self.load_invoices()
            messagebox.showinfo("Success", "Invoice marked as unpaid!")
        else:
            messagebox.showwarning("Error", "Please select an invoice to mark as unpaid.")

    # Mark an invoice as paid
    def mark_as_paid(self):
        selected_item = self.invoice_list.selection()
        if selected_item:
            invoice_id = self.invoice_list.item(selected_item)['values'][0]
            cursor.execute("UPDATE invoices SET status='paid' WHERE id=?", (invoice_id,))
            conn.commit()
            self.load_invoices()
            messagebox.showinfo("Success", "Invoice marked as paid!")
        else:
            messagebox.showwarning("Error", "Please select an invoice to mark as paid.")

    # Delete an invoice
    def delete_invoice(self):
        selected_item = self.invoice_list.selection()
        if selected_item:
            invoice_id = self.invoice_list.item(selected_item)['values'][0]
            if messagebox.askyesno("Delete Invoice", f"Are you sure you want to delete invoice #{invoice_id}?"):
                cursor.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
                conn.commit()
                self.load_invoices()
                messagebox.showinfo("Success", "Invoice deleted successfully!")
            else:
                messagebox.showwarning("Error", "Please select an invoice to delete.")

    # Generate HTML invoice and open it in browser
    def print_invoice(self):
        selected_item = self.invoice_list.selection()
        if selected_item:
            invoice_id = self.invoice_list.item(selected_item)['values'][0]
            cursor.execute("""
                SELECT invoices.*, clients.* 
                FROM invoices 
                JOIN clients ON invoices.client_id = clients.id
                WHERE invoices.id=?""", (invoice_id,))
            invoice = cursor.fetchone()
            if invoice:
                self.generate_html_invoice(invoice)
        else:
            messagebox.showwarning("Error", "Please select an invoice to print.")

    # Generate the HTML file for the invoice
    def generate_html_invoice(self, invoice):
        invoice_date = datetime.strptime(invoice[4], "%Y-%m-%d")
        due_date = invoice_date + timedelta(days=30)
        subtotal = float(invoice[3])

        # GST rate is 5%
        gst_rate = 0.05
        tax = subtotal * gst_rate
        total = subtotal + tax

        # Read the HTML template
        with open('invoice.html', 'r') as file:
            html_template = file.read()

        # Parse line items
        line_items_html = ""
        for line in invoice[2].strip().split('\n'):
            item, details = line.split(':', 1)
            quantity, price_total = details.split('@')
            price, line_items_total = price_total.split('=')
            print('{' +quantity+ '}')
            if quantity != ' 0.0 ':
                line_items_html += f"""
                <tr>
                    <td>{quantity.strip()}</td>
                    <td>{item.strip()}</td>
                    <td class="right">{price.strip()}</td>
                    <td class="right">{line_items_total.strip()}</td>
                </tr>
                """

        # Prepare the context for the template
        context = {
            "invoice_number": invoice[0],
            "invoice_date": invoice_date.strftime("%B %d, %Y"),
            "due_date": due_date.strftime("%B %d, %Y"),
            "client_name": invoice[7],
            "client_address": invoice[8],
            "client_contact": invoice[9],
            "client_phone": invoice[10],
            "client_email": invoice[11],
            "company_name": self.preferences.get('company_name', 'Your Company Name'),
            "company_address": self.preferences.get('company_address', 'Your Company Address'),
            "company_city": self.preferences.get('company_city', ''),
            "company_state": self.preferences.get('company_state', ''),
            "company_postal": self.preferences.get('company_postal', ''),
            "gst_number": self.preferences.get('gst_number', ''),
            "company_phone": self.preferences.get('company_phone', ''),
            "company_email": self.preferences.get('company_email', ''),
            "company_website": self.preferences.get('company_website', ''),
            "line_items": line_items_html,
            "subtotal": f"${subtotal:.2f}",
            "tax": f"${tax:.2f}",
            "total": f"${total:.2f}"
        }

        # Replace placeholders in the template
        for key, value in context.items():
            placeholder = '{{' + key + '}}'
            html_template = html_template.replace(placeholder, str(value))

        filename = f"invoice_{invoice[0]}.html"
        with open(filename, "w") as file:
            file.write(html_template)

        # Open the generated HTML file in the default browser
        webbrowser.open(f"file://{os.path.realpath(filename)}")

    # Clear form fields
    def clear_fields(self):
        self.client_var.set("")
        for qty_var in self.qty_vars:
            qty_var.set("0")

# Run the app
if __name__ == "__main__":
    app = InvoiceApp()
    app.mainloop()

    # Close the database connection when the app is closed
    conn.close()

