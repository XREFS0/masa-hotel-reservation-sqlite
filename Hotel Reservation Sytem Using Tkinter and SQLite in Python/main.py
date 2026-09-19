"""
Developed by MASA
All Rights Reserved.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

conn = sqlite3.connect("hotel_system.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT,
    room_number TEXT,
    check_in TEXT,
    check_out TEXT,
    contact TEXT
)
""")

cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin','admin123','admin')")
conn.commit()

root = tk.Tk()
root.title("MASA - Hotel Reservation System")
root.geometry("400x300")  # Small login window
root.resizable(False, False)
root.configure(bg="#f4f6f8")

selected_id = None


def valid_date(d):
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except:
        return False


username = tk.StringVar()
password = tk.StringVar()


def create_login_screen():
    global login_frame
    login_frame = tk.Frame(root, bg="#f4f6f8")
    login_frame.pack(expand=True)

    tk.Label(login_frame, text="HOTEL SYSTEM", font=("Segoe UI", 20, "bold"), bg="#f4f6f8").pack(pady=20)
    tk.Entry(login_frame, textvariable=username, width=28).pack(pady=6)
    tk.Entry(login_frame, textvariable=password, show="*", width=28).pack(pady=6)
    tk.Button(
        login_frame, text="Login", width=18, bg="#2c3e50", fg="white", relief="flat", command=login
    ).pack(pady=15)


def login():
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username.get(), password.get()))
    if cursor.fetchone():
        login_frame.destroy()
        username.set("")  # Clear username field
        password.set("")  # Clear password field
        create_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")


def create_dashboard():
    global dashboard_frame, guest, room, checkin, checkout, contact
    global btn_add, btn_update, btn_delete, btn_clear
    global search_var, tree, ax, canvas

    dashboard_frame = tk.Frame(root, bg="#ecf0f1")
    dashboard_frame.pack(fill="both", expand=True)
    root.geometry("1300x750")
    root.resizable(True, True)

    guest = tk.StringVar()
    room = tk.StringVar()
    checkin = tk.StringVar()
    checkout = tk.StringVar()
    contact = tk.StringVar()
    search_var = tk.StringVar()

    header = tk.Frame(dashboard_frame, bg="#2c3e50", height=60)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Hotel Reservation Management System",
        bg="#2c3e50",
        fg="white",
        font=("Segoe UI", 18, "bold"),
    ).pack(side="left", padx=20)
    tk.Button(header, text="Logout", bg="#e74c3c", fg="white", relief="flat", command=logout).pack(
        side="right", padx=20
    )

    main_frame = tk.Frame(dashboard_frame, bg="#ecf0f1")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    form_frame = tk.LabelFrame(
        main_frame,
        text="Reservation Form",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="black",
        padx=10,
        pady=10,
    )
    form_frame.pack(side="left", fill="y", padx=5, pady=5)

    labels = ["Guest Name", "Room Number", "Check-in (YYYY-MM-DD)", "Check-out (YYYY-MM-DD)", "Contact"]
    vars_ = [guest, room, checkin, checkout, contact]

    for i, (lbl, var) in enumerate(zip(labels, vars_)):
        tk.Label(form_frame, text=lbl, bg="white").grid(row=i, column=0, sticky="w", pady=4)
        tk.Entry(form_frame, textvariable=var, width=25).grid(row=i, column=1, pady=4)

    btn_add = tk.Button(form_frame, text="Add", bg="#27ae60", fg="white", width=12, command=add_reservation)
    btn_add.grid(row=0, column=2, padx=5)
    btn_update = tk.Button(
        form_frame,
        text="Update",
        bg="#2980b9",
        fg="white",
        width=12,
        command=update_reservation,
        state="disabled",
    )
    btn_update.grid(row=1, column=2, padx=5)
    btn_delete = tk.Button(
        form_frame,
        text="Delete",
        bg="#c0392b",
        fg="white",
        width=12,
        command=delete_reservation,
        state="disabled",
    )
    btn_delete.grid(row=2, column=2, padx=5)
    btn_clear = tk.Button(form_frame, text="Clear", bg="#7f8c8d", fg="white", width=12, command=clear_form)
    btn_clear.grid(row=3, column=2, padx=5)

    search_frame = tk.Frame(main_frame, bg="#ecf0f1")
    search_frame.pack(side="top", fill="x", pady=5)

    tk.Label(search_frame, text="Search:", bg="#ecf0f1").pack(side="left", padx=5)
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side="left", padx=5)
    search_var.trace("w", search_table)

    chart_frame = tk.LabelFrame(
        main_frame,
        text="Room Usage Chart",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="black",
        padx=10,
        pady=10,
    )
    chart_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, chart_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    table_frame = tk.Frame(dashboard_frame)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
    x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
    y_scroll.pack(side="right", fill="y")
    x_scroll.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        table_frame,
        columns=("ID", "Guest", "Room", "Check-in", "Check-out", "Contact"),
        show="headings",
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set,
    )
    tree.pack(fill="both", expand=True)
    y_scroll.config(command=tree.yview)
    x_scroll.config(command=x_scroll.set)

    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center", stretch=False)
    tree.column("Guest", width=200)
    tree.column("Contact", width=200)

    tree.bind("<Double-1>", populate_on_double_click)
    tree.bind("<<TreeviewSelect>>", select_row_single_click)

    load_table()
    update_chart()


def clear_form():
    global selected_id
    selected_id = None
    guest.set("")
    room.set("")
    checkin.set("")
    checkout.set("")
    contact.set("")
    btn_add.config(state="normal")
    btn_update.config(state="disabled")
    btn_delete.config(state="disabled")
    tree.selection_remove(tree.selection())


def add_reservation():
    if not valid_date(checkin.get()) or not valid_date(checkout.get()):
        messagebox.showerror("Error", "Use YYYY-MM-DD format")
        return
    cursor.execute(
        """
        INSERT INTO reservations VALUES (NULL,?,?,?,?,?)
    """,
        (guest.get(), room.get(), checkin.get(), checkout.get(), contact.get()),
    )
    conn.commit()
    load_table()
    update_chart()
    clear_form()


def update_reservation():
    global selected_id
    if not selected_id:
        messagebox.showwarning("Select Row", "Please select a reservation")
        return
    cursor.execute(
        """
        UPDATE reservations SET guest_name=?, room_number=?, check_in=?, check_out=?, contact=?
        WHERE id=?
    """,
        (guest.get(), room.get(), checkin.get(), checkout.get(), contact.get(), selected_id),
    )
    conn.commit()
    load_table()
    update_chart()
    clear_form()


def delete_reservation():
    global selected_id
    if not selected_id:
        messagebox.showwarning("Select Row", "Please select a reservation")
        return
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete?"):
        cursor.execute("DELETE FROM reservations WHERE id=?", (selected_id,))
        conn.commit()
        load_table()
        update_chart()
        clear_form()


def logout():
    dashboard_frame.destroy()
    root.geometry("400x300")  # Reset login window size
    root.resizable(False, False)
    create_login_screen()


def load_table():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM reservations")
    for i, rec in enumerate(cursor.fetchall()):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=rec, tags=(tag,))
    tree.tag_configure("even", background="#f2f2f2")
    tree.tag_configure("odd", background="white")


def populate_on_double_click(event):
    global selected_id
    row_id = tree.identify_row(event.y)
    if row_id:
        values = tree.item(row_id, "values")
        selected_id = values[0]
        guest.set(values[1])
        room.set(values[2])
        checkin.set(values[3])
        checkout.set(values[4])
        contact.set(values[5])
        btn_add.config(state="disabled")
        btn_update.config(state="normal")
        btn_delete.config(state="normal")


def select_row_single_click(event):
    global selected_id
    selected = tree.selection()
    if selected:
        values = tree.item(selected[0], "values")
        selected_id = values[0]
        btn_delete.config(state="normal")
    else:
        btn_delete.config(state="disabled")


def search_table(*args):
    term = search_var.get().lower()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM reservations")
    for rec in cursor.fetchall():
        if term in rec[1].lower() or term in rec[2].lower():
            tree.insert("", "end", values=rec)
    load_table()


def update_chart():
    cursor.execute("SELECT room_number, COUNT(*) FROM reservations GROUP BY room_number")
    data = cursor.fetchall()
    ax.clear()
    if data:
        occupied_rooms = len(data)
        total_rooms = 10
        labels = ["Occupied", "Available"]
        sizes = [occupied_rooms, total_rooms - occupied_rooms]
        colors = ["#e74c3c", "#2ecc71"]
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
    canvas.draw()


create_login_screen()
root.mainloop()
