import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
import detect
import camera
import sqlite3

# Insert data into SQLite database
conn = sqlite3.connect('license_plates.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS license_plates
                (plate_number TEXT UNIQUE, name TEXT, phone TEXT, category TEXT)''')
conn.commit()
conn.close()
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
    detected_plate_number = camera.detect_plate()
    if detected_plate_number:
        detection_result_entry.configure(state='normal')
        detection_result_entry.delete(0, tk.END)
        detection_result_entry.insert(0, detected_plate_number)
        detection_result_entry.configure(state='readonly')
    else:
        messagebox.showinfo("No Plate Detected", "No license plate detected in the image.")
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
category_combobox = ttk.Combobox(add_tab, values=["Staff", "Student", "Teacher"], width=27)
category_combobox.grid(row=3, column=1)

# Button to add license plate
add_button = ttk.Button(add_tab, text="Add License Plate", command=add_license_plate)
add_button.grid(row=5, column=1, sticky=tk.E)

detect_button = ttk.Button(add_tab, text="Capture Plate", command=captured)
detect_button.grid(row=4, column=1, sticky=tk.E)
# Start the Tkinter event loop

# Tab 3: Detection
detection_tab = ttk.Frame(notebook)
notebook.add(detection_tab, text='Detection')

# Add widgets for detection functionality
detection_label = ttk.Label(detection_tab, text="Click the button below to detect license plates:")
detection_label.grid(row=0, column=0, padx=10, pady=10)

detect_button = ttk.Button(detection_tab, text="Detect Plates", command=detect_plates)
detect_button.grid(row=1, column=0, padx=10, pady=10)

detection_result_label = ttk.Label(detection_tab, text="Detected Plate Number:")
detection_result_label.grid(row=2, column=0, padx=10, pady=10)

detection_result_entry = ttk.Entry(detection_tab, width=30, state='readonly')
detection_result_entry.grid(row=3, column=0, padx=10, pady=10)




populate_license_plates()
root.mainloop()