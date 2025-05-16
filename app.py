import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import re

# === Data classes (similar to your original code) ===
class Book:
    def __init__(self, title, author, isbn, is_ebook=False, ebook_url=''):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_lent = False
        self.due_date = None
        self.borrower = None
        self.is_ebook = is_ebook
        self.ebook_url = ebook_url

    def lend(self, borrower):
        if self.is_lent:
            raise Exception("Book is already lent.")
        self.is_lent = True
        self.borrower = borrower
        self.due_date = datetime.today() + timedelta(days=7)

    def return_book(self):
        if not self.is_lent:
            raise Exception("Book is not lent.")
        self.is_lent = False
        self.borrower = None
        self.due_date = None

    def __str__(self):
        status = "Available" if not self.is_lent else f"Lent to {self.borrower} (Due {self.due_date.date()})"
        ebook_info = f" [eBook: {self.ebook_url}]" if self.is_ebook else ""
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - {status}{ebook_info}"

class User:
    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = password
        self.role = role

class Library:
    def __init__(self):
        self.books = []
        self.users = {}

    def register_user(self, username, password, role='user'):
        if username in self.users:
            raise Exception("User already registered.")
        self.users[username] = User(username, password, role)

    def authenticate(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            return user
        return None

    def add_book(self, book):
        if any(b.isbn == book.isbn for b in self.books):
            raise Exception("Book already exists.")
        self.books.append(book)

    def remove_book(self, isbn):
        self.books = [b for b in self.books if b.isbn != isbn]

    def lend_book(self, isbn, borrower):
        for book in self.books:
            if book.isbn == isbn:
                book.lend(borrower)
                return
        raise Exception("Book not found.")

    def return_book(self, isbn):
        for book in self.books:
            if book.isbn == isbn:
                book.return_book()
                return
        raise Exception("Book not found.")

    def available_books(self):
        return [book for book in self.books if not book.is_lent]

    def books_by_author(self, author_name):
        return [book for book in self.books if book.author.lower() == author_name.lower()]


# === Main GUI application ===
class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.library = Library()

        # Pre-register default users
        self.library.register_user("admin", "admin123", "admin")
        self.library.register_user("user1", "pass1", "user")

        self.title("Library Management System")
        self.geometry("600x500")

        # Container frame to hold all screens
        self.container = ttk.Frame(self)
        self.container.pack(fill='both', expand=True)

        # Dictionary of frames/screens
        self.frames = {}

        # Current logged in user
        self.current_user = None

        # Initialize all frames
        for F in (LoginScreen, RegisterScreen, UserMenu, AdminMenu, AddBookScreen):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(LoginScreen)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# --- Login Screen ---
class LoginScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Login", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Password:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        login_button = ttk.Button(self, text="Login", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=10)

        register_button = ttk.Button(self, text="Register", command=lambda: controller.show_frame(RegisterScreen))
        register_button.grid(row=4, column=0, columnspan=2, pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user = self.controller.library.authenticate(username, password)
        if user:
            self.controller.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user.username}!")

            if user.role == 'admin':
                self.controller.show_frame(AdminMenu)
            else:
                self.controller.show_frame(UserMenu)
            # Clear inputs
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", "Invalid username or password.")

# --- Register Screen ---
class RegisterScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Register", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Password:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Role (admin/user):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.role_entry = ttk.Combobox(self, values=["admin", "user"])
        self.role_entry.grid(row=3, column=1, padx=5, pady=5)
        self.role_entry.current(1)  # Default to user

        register_button = ttk.Button(self, text="Register", command=self.register)
        register_button.grid(row=4, column=0, columnspan=2, pady=10)

        back_button = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame(LoginScreen))
        back_button.grid(row=5, column=0, columnspan=2, pady=5)

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_entry.get().strip().lower()

        if role not in ['admin', 'user']:
            role = 'user'

        try:
            self.controller.library.register_user(username, password, role)
            messagebox.showinfo("Success", "Registration successful. Please login.")
            self.controller.show_frame(LoginScreen)
            # Clear fields
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", str(e))


# --- User Menu Screen ---
class UserMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="User Menu", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Button(self, text="Show Available Books", command=self.show_books).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(self, text="Borrow Book", command=self.borrow_book).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(self, text="Return Book", command=self.return_book).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(self, text="Show Books by Author", command=self.show_books_by_author).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(self, text="Logout", command=self.logout).grid(row=2, column=2, padx=10, pady=5)

        self.output = tk.Text(self, height=15, width=70, state='disabled')
        self.output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def show_books(self):
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)
        books = self.controller.library.available_books()
        if not books:
            self.output.insert(tk.END, "No available books.\n")
        else:
            for book in books:
                self.output.insert(tk.END, str(book) + "\n")
        self.output.config(state='disabled')

    def borrow_book(self):
        isbn = simple_input_dialog(self, "Borrow Book", "Enter ISBN to borrow:")
        if isbn:
            try:
                self.controller.library.lend_book(isbn, self.controller.current_user.username)
                messagebox.showinfo("Success", "Book borrowed successfully.")
                self.show_books()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def return_book(self):
        isbn = simple_input_dialog(self, "Return Book", "Enter ISBN to return:")
        if isbn:
            try:
                self.controller.library.return_book(isbn)
                messagebox.showinfo("Success", "Book returned successfully.")
                self.show_books()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_books_by_author(self):
        author = simple_input_dialog(self, "Books by Author", "Enter author name:")
        if author:
            books = self.controller.library.books_by_author(author)
            self.output.config(state='normal')
            self.output.delete('1.0', tk.END)
            if not books:
                self.output.insert(tk.END, f"No books found by author '{author}'.\n")
            else:
                for book in books:
                    self.output.insert(tk.END, str(book) + "\n")
            self.output.config(state='disabled')

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginScreen)

# --- Admin Menu Screen ---
class AdminMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Admin Menu", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Button(self, text="Add Book", command=lambda: controller.show_frame(AddBookScreen)).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(self, text="Remove Book", command=self.remove_book).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(self, text="Show All Books", command=self.show_books).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(self, text="Logout", command=self.logout).grid(row=2, column=2, padx=10, pady=5)

        self.output = tk.Text(self, height=15, width=70, state='disabled')
        self.output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def remove_book(self):
        isbn = simple_input_dialog(self, "Remove Book", "Enter ISBN to remove:")
        if isbn:
            self.controller.library.remove_book(isbn)
            messagebox.showinfo("Success", "Book removed.")
            self.show_books()

    def show_books(self):
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)
        if not self.controller.library.books:
            self.output.insert(tk.END, "No books in library.\n")
        else:
            for book in self.controller.library.books:
                self.output.insert(tk.END, str(book) + "\n")
        self.output.config(state='disabled')

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginScreen)


# --- Add Book Screen (with eBook checkbox + validation) ---
class AddBookScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Add Book", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Title:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.title_entry = ttk.Entry(self, width=40)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Author:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.author_entry = ttk.Entry(self, width=40)
        self.author_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="ISBN:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.isbn_entry = ttk.Entry(self, width=40)
        self.isbn_entry.grid(row=3, column=1, padx=5, pady=5)

        self.ebook_var = tk.BooleanVar()
        self.ebook_check = ttk.Checkbutton(self, text="Is eBook?", variable=self.ebook_var, command=self.toggle_ebook)
        self.ebook_check.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(self, text="eBook URL:").grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.ebook_entry = ttk.Entry(self, width=40, state='disabled')
        self.ebook_entry.grid(row=5, column=1, padx=5, pady=5)

        add_button = ttk.Button(self, text="Add Book", command=self.add_book)
        add_button.grid(row=6, column=0, columnspan=2, pady=10)

        back_button = ttk.Button(self, text="Back", command=lambda: controller.show_frame(AdminMenu))
        back_button.grid(row=7, column=0, columnspan=2)

    def toggle_ebook(self):
        if self.ebook_var.get():
            self.ebook_entry.config(state='normal')
        else:
            self.ebook_entry.delete(0, tk.END)
            self.ebook_entry.config(state='disabled')

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        is_ebook = self.ebook_var.get()
        ebook_url = self.ebook_entry.get().strip()

        if not title or not author or not isbn:
            messagebox.showerror("Error", "Title, Author and ISBN are required.")
            return

        if is_ebook:
            # Simple URL validation
            if not re.match(r'^https?://\S+\.\S+$', ebook_url):
                messagebox.showerror("Error", "Enter a valid eBook URL (starting with http:// or https://)")
                return
        else:
            ebook_url = ""

        try:
            new_book = Book(title, author, isbn, is_ebook, ebook_url)
            self.controller.library.add_book(new_book)
            messagebox.showinfo("Success", "Book added successfully.")
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_entries(self):
        self.title_entry.delete(0, 'end')
        self.author_entry.delete(0, 'end')
        self.isbn_entry.delete(0, 'end')
        self.ebook_var.set(False)
        self.ebook_entry.delete(0, 'end')
        self.ebook_entry.config(state='disabled')


# --- Helper dialog for input ---
def simple_input_dialog(parent, title, prompt):
    input_win = tk.Toplevel(parent)
    input_win.title(title)
    input_win.geometry("300x120")
    input_win.grab_set()

    ttk.Label(input_win, text=prompt).pack(pady=10)
    entry = ttk.Entry(input_win, width=30)
    entry.pack(pady=5)

    value = {'text': None}

    def submit():
        value['text'] = entry.get().strip()
        input_win.destroy()

    submit_btn = ttk.Button(input_win, text="Submit", command=submit)
    submit_btn.pack(pady=5)

    parent.wait_window(input_win)
    return value['text']


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
