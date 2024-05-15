import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
import detect
import camera
import sqlite3
import serial

ser = serial.serial_for_url('rfc2217://localhost:4000', baudrate=115200)

def create_history_table():
    hConn = sqlite3.connect('history.db')
    h = hConn.cursor()
    h.execute('''CREATE TABLE IF NOT EXISTS history_table
                 (plate_number TEXT, Name TEXT, Phone TEXT, Role TEXT, timestamp DATETIME)''')
    hConn.commit()
    hConn.close()

def create_main_table():
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS license_plates
                    (plate_number TEXT UNIQUE, name TEXT, phone TEXT, category TEXT)''')
    conn.commit()
    conn.close()


create_main_table()
create_history_table()

# Function to add a new license plate record to the database
def add_license_plate():
    # Retrieve data from entry widgets
    plate_number = plate_number_entry.get()
    name = name_entry.get()
    phone = phone_entry.get()
    category = category_combobox.get()

    # Check if any field is empty
    if not (plate_number and name and phone):
        messagebox.showerror("showerror", "Please fill all fields!") 


        return

    # Insert data into SQLite database
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()
    c.execute("INSERT INTO license_plates VALUES (?, ?, ?, ?)", (plate_number, name, phone, category))
    conn.commit()
    conn.close()
    populate_license_plates()

    # Clear entry widgets after adding the record
    plate_number_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    category_combobox.set('')  # Reset combobox selection


# Function to populate the history tab with records

def populate_history():
    # Clear existing rows in the treeview
    for row in history_tree.get_children():
        history_tree.delete(row)

    # Connect to SQLite database
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Fetch data from database
    c.execute("SELECT plate_number, Name, Phone, Role, timestamp FROM history_table")
    rows = c.fetchall()

    # Insert data into treeview
    for row in rows:
        history_tree.insert('', 'end', values=row)

    # Close database connection
    conn.close()

# Function to populate the license plates tab with records
def populate_license_plates():
    # Clear existing rows in the treeview
    for row in license_plate_tree.get_children():
        license_plate_tree.delete(row)

    # Fetch data from SQLite database
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()
    c.execute("SELECT * FROM license_plates")
    rows = c.fetchall()
    conn.close()

    # Insert data into treeview
    for row in rows:
        license_plate_tree.insert('', 'end', values=row)

# Function to delete selected record
def delete_selected_record():
    # Get the selected item
    selected_item = license_plate_tree.selection()
    if not selected_item:
        return

    # Get the license plate number from the selected item
    plate_number = license_plate_tree.item(selected_item)['values'][0]

    # Delete record from SQLite database
    conn = sqlite3.connect('license_plates.db')
    c = conn.cursor()
    c.execute("DELETE FROM license_plates WHERE plate_number=?", (plate_number,))
    conn.commit()
    conn.close()

    # Refresh the license plates tab
    populate_license_plates()

def captured():
    v = detect.detect_plate()
    plate_number_entry.delete(0, tk.END)
    plate_number_entry.insert(0, v)

# Function to detect license plates
def detect_plates():
    camera.detect_plate(populate_history)
# Function to search history records
def search_history():
    # Get search criteria from entry widgets
    plate_query = plate_search_entry.get().strip()
    name_query = name_search_entry.get().strip()
    phone_query = phone_search_entry.get().strip()

    # Clear existing rows in the treeview
    for row in history_tree.get_children():
        history_tree.delete(row)

    # Connect to SQLite database
    conn = sqlite3.connect('history.db')
    c = conn.cursor()

    # Construct SQL query based on search criteria
    query = "SELECT plate_number, Name, Phone, timestamp FROM history_table WHERE "
    conditions = []
    if plate_query:
        conditions.append(f"plate_number LIKE '%{plate_query}%'")
    if name_query:
        conditions.append(f"Name LIKE '%{name_query}%'")
    if phone_query:
        conditions.append(f"Phone LIKE '%{phone_query}%'")

    if conditions:
        query += " AND ".join(conditions)
    else:
        query += "1"  # Add dummy condition to avoid syntax error

    # Fetch data from database based on search query
    c.execute(query)
    rows = c.fetchall()

    # Insert filtered data into treeview
    for row in rows:
        history_tree.insert('', 'end', values=row)

    # Close database connection
    conn.close()


# Create main window
root = tk.Tk()
root.title("License Plate Manager")

# Set style
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", padding=10, font=('Helvetica', 10))
style.configure("TLabel", padding=10, font=('Helvetica', 10))
style.configure("TEntry", padding=10, font=('Helvetica', 10))
style.configure("Treeview", font=('Helvetica', 10))

# Create notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Tab 1: View License Plates
view_tab = ttk.Frame(notebook)
notebook.add(view_tab, text='View License Plates')

# Create and pack a frame for the input fields
input_frame = ttk.Frame(view_tab, padding="10")
input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# License Plate Treeview
license_plate_tree = ttk.Treeview(view_tab, columns=('Plate Number', 'Name', 'Phone', 'Category'), show='headings')
license_plate_tree.heading('Plate Number', text='Plate Number')
license_plate_tree.heading('Name', text='Name')
license_plate_tree.heading('Phone', text='Phone')
license_plate_tree.heading('Category', text='Category')

license_plate_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Button to populate the license plates tab
populate_button = ttk.Button(view_tab, text="Refresh", command=populate_license_plates)
populate_button.grid(row=2, column=0, sticky=tk.W)

# Button to delete selected record
delete_button = ttk.Button(view_tab, text="Delete", command=delete_selected_record)
delete_button.grid(row=2, column=0, sticky=tk.E)

# Tab 2: Add New Record
add_tab = ttk.Frame(notebook)
notebook.add(add_tab, text='Add New Record')

# License Plate Number
plate_number_label = ttk.Label(add_tab, text="License Plate Number:")
plate_number_label.grid(row=0, column=0, sticky=tk.W)
plate_number_entry = ttk.Entry(add_tab, width=30)
plate_number_entry.grid(row=0, column=1)

# Name
name_label = ttk.Label(add_tab, text="Name:")
name_label.grid(row=1, column=0, sticky=tk.W)
name_entry = ttk.Entry(add_tab, width=30)
name_entry.grid(row=1, column=1)

# Phone
phone_label = ttk.Label(add_tab, text="Phone:")
phone_label.grid(row=2, column=0, sticky=tk.W)
phone_entry = ttk.Entry(add_tab, width=30)
phone_entry.grid(row=2, column=1)


# Category
category_label = ttk.Label(add_tab, text="Category:")
category_label.grid(row=3, column=0, sticky=tk.W)
category_combobox = ttk.Combobox(add_tab, values=["Directeur/Staff", "Service Technique d'intervention GAZ", "Service Technique d'intervention ELEC"], width=27)
category_combobox.grid(row=3, column=1)

# Button to add license plate
add_button = ttk.Button(add_tab, text="Add License Plate", command=add_license_plate)
add_button.grid(row=5, column=1, sticky=tk.E)

detect_button = ttk.Button(add_tab, text="Capture Plate", command=captured)
detect_button.grid(row=4, column=1, sticky=tk.E)

# Tab 3: Detection
detection_tab = ttk.Frame(notebook)
notebook.add(detection_tab, text='Detection')

# Add widgets for detection functionality
detection_label = ttk.Label(detection_tab, text="Click the button below to detect license plates:")
detection_label.grid(row=0, column=0, padx=10, pady=10)

detect_button = ttk.Button(detection_tab, text="Detect Plates", command=detect_plates)
detect_button.grid(row=1, column=0, padx=10, pady=10)

# Tab 4: History
history_tab = ttk.Frame(notebook)
notebook.add(history_tab, text='History')

# Create Treeview for displaying history records
history_tree = ttk.Treeview(history_tab, columns=('Plate Number', 'Name', 'Phone', 'Role', 'Timestamp'), show='headings')
history_tree.heading('Plate Number', text='Plate Number')
history_tree.heading('Name', text='Name')
history_tree.heading('Phone', text='Phone')
history_tree.heading('Role', text='Role')
history_tree.heading('Timestamp', text='Timestamp')
history_tree.pack(fill='both', expand=True)


# Create entry widgets for search queries
# Create entry widgets for search queries
plate_search_label = ttk.Label(history_tab, text="Search by License Plate:")
plate_search_label.pack(side=tk.LEFT, padx=5)

plate_search_entry = ttk.Entry(history_tab, width=20)
plate_search_entry.pack(side=tk.LEFT, padx=5)

name_search_label = ttk.Label(history_tab, text="Search by Name:")
name_search_label.pack(side=tk.LEFT, padx=5)

name_search_entry = ttk.Entry(history_tab, width=20)
name_search_entry.pack(side=tk.LEFT, padx=5)

phone_search_label = ttk.Label(history_tab, text="Search by Phone:")
phone_search_label.pack(side=tk.LEFT, padx=5)

phone_search_entry = ttk.Entry(history_tab, width=20)
phone_search_entry.pack(side=tk.LEFT, padx=5)
# Button to trigger search
search_button = ttk.Button(history_tab, text="Search", command=search_history)
search_button.pack(side=tk.LEFT, padx=10)
populate_license_plates()
populate_history()
root.mainloop()
