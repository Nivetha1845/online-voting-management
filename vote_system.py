import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# ---------------- Database Setup ---------------- #
conn = sqlite3.connect("voting.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS voters (
                    voter_id TEXT PRIMARY KEY,
                    name TEXT,
                    password TEXT,
                    voted INTEGER DEFAULT 0)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    votes INTEGER DEFAULT 0)""")
conn.commit()


# ---------------- Functions ---------------- #
def add_candidate():
    name = simpledialog.askstring("Add Candidate", "Enter candidate name:")
    if name:
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (name,))
        conn.commit()
        messagebox.showinfo("Success", f"Candidate '{name}' added successfully!")


def add_voter():
    voter_id = simpledialog.askstring("Add Voter", "Enter voter ID:")
    name = simpledialog.askstring("Add Voter", "Enter voter name:")
    password = simpledialog.askstring("Add Voter", "Enter password:")
    if voter_id and name and password:
        try:
            cursor.execute("INSERT INTO voters (voter_id, name, password) VALUES (?, ?, ?)",
                           (voter_id, name, password))
            conn.commit()
            messagebox.showinfo("Success", f"Voter '{name}' added successfully!")
        except:
            messagebox.showerror("Error", "Voter ID already exists!")


def voter_login():
    voter_id = voter_id_var.get()
    password = password_var.get()
    cursor.execute("SELECT * FROM voters WHERE voter_id=? AND password=?", (voter_id, password))
    voter = cursor.fetchone()
    if voter:
        if voter[3] == 1:
            messagebox.showwarning("Error", "You have already voted!")
        else:
            open_voting_window(voter_id, voter[1])
    else:
        messagebox.showerror("Error", "Invalid Login!")


def open_voting_window(voter_id, voter_name):
    vote_win = tk.Toplevel(root)
    vote_win.title("Cast Your Vote")
    tk.Label(vote_win, text=f"Welcome {voter_name}, Please select a candidate:",
             font=("Arial", 12)).pack(pady=10)

    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    selected = tk.IntVar()
    for c in candidates:
        tk.Radiobutton(vote_win, text=c[1], variable=selected, value=c[0]).pack(anchor="w")

    def submit_vote():
        cid = selected.get()
        if cid == 0:
            messagebox.showwarning("Error", "Please select a candidate!")
            return
        cursor.execute("UPDATE candidates SET votes=votes+1 WHERE candidate_id=?", (cid,))
        cursor.execute("UPDATE voters SET voted=1 WHERE voter_id=?", (voter_id,))
        conn.commit()
        messagebox.showinfo("Success", "Your vote has been recorded!")
        vote_win.destroy()

    tk.Button(vote_win, text="Submit Vote", command=submit_vote, bg="green", fg="white").pack(pady=10)


def show_results():
    result_win = tk.Toplevel(root)
    result_win.title("Election Results")

    cols = ("Candidate", "Votes")
    tree = ttk.Treeview(result_win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    cursor.execute("SELECT name, votes FROM candidates")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)


# ---------------- Main GUI ---------------- #
root = tk.Tk()
root.title("Online Voting System")
root.geometry("400x300")

# Login Frame
frame_login = tk.LabelFrame(root, text="Voter Login", padx=10, pady=10)
frame_login.pack(fill="x", padx=20, pady=20)

tk.Label(frame_login, text="Voter ID").grid(row=0, column=0, padx=5, pady=5)
voter_id_var = tk.StringVar()
tk.Entry(frame_login, textvariable=voter_id_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_login, text="Password").grid(row=1, column=0, padx=5, pady=5)
password_var = tk.StringVar()
tk.Entry(frame_login, textvariable=password_var, show="*").grid(row=1, column=1, padx=5, pady=5)

tk.Button(frame_login, text="Login", command=voter_login, bg="blue", fg="white").grid(row=2, column=0, columnspan=2, pady=10)

# Admin Buttons
frame_admin = tk.LabelFrame(root, text="Admin Panel", padx=10, pady=10)
frame_admin.pack(fill="x", padx=20, pady=10)

tk.Button(frame_admin, text="Add Candidate", command=add_candidate, bg="orange").pack(side="left", padx=10)
tk.Button(frame_admin, text="Add Voter", command=add_voter, bg="orange").pack(side="left", padx=10)
tk.Button(frame_admin, text="Show Results", command=show_results, bg="green", fg="white").pack(side="left", padx=10)

root.mainloop()
