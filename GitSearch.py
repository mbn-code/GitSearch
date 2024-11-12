import tkinter as tk
from tkinter import ttk
import webbrowser
import requests

# Font settings
FONT_FAMILY = "Helvetica Neue"
FONT_SIZE = 12

# Theme settings
THEME_STYLE = "clam"

def get_repositories(query, sort_by, language_filter):
    # [Function code remains the same]
    pass

def perform_search(sort_by=None):
    # [Function code remains the same]
    pass

# Create the main window
window = tk.Tk()
window.title('GitHub Search')

# Configure the window size and position
window.geometry("1000x700")
window.resizable(True, True)

# Set dark mode colors
BACKGROUND_COLOR = "#1e1e1e"
FOREGROUND_COLOR = "#ffffff"
ACCENT_COLOR = "#0a84ff"

# Configure the window background
window.configure(bg=BACKGROUND_COLOR)

# Create a style for the GUI elements
style = ttk.Style()
style.theme_use(THEME_STYLE)

# Configure styles for dark mode
style.configure('.', background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR, font=(FONT_FAMILY, FONT_SIZE))
style.configure('TLabel', background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
style.configure('TEntry', fieldbackground="#2c2c2e", foreground=FOREGROUND_COLOR, bordercolor="#3a3a3c")
style.configure('TButton', background=ACCENT_COLOR, foreground=FOREGROUND_COLOR)
style.map('TButton', background=[('active', '#0060df')])

# Create a frame to hold the content
content_frame = ttk.Frame(window, padding=20)
content_frame.pack(fill="both", expand=True)

# Create a label and entry for the search query
label = ttk.Label(content_frame, text='Enter a search query:')
label.grid(row=0, column=0, sticky="w", pady=10, padx=10)

entry = ttk.Entry(content_frame)
entry.grid(row=0, column=1, sticky="we", pady=10, padx=10)

# Create a combobox for language selection
language_label = ttk.Label(content_frame, text='Filter by language:')
language_label.grid(row=0, column=2, sticky="w", pady=10, padx=10)

language_var = tk.StringVar()
language_combobox = ttk.Combobox(content_frame, textvariable=language_var, state='readonly')
language_combobox['values'] = ['', 'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Ruby', 'Swift']
language_combobox.current(0)
language_combobox.grid(row=0, column=3, sticky="we", pady=10, padx=10)

# Create a button to perform the search
button = ttk.Button(content_frame, text='Search', command=lambda: perform_search(sort_var.get()))
button.grid(row=0, column=4, sticky="e", pady=10, padx=10)

# Create radio buttons for sorting options
sort_var = tk.StringVar(value='')
sort_frame = ttk.LabelFrame(content_frame, text='Sort Options')
sort_frame.grid(row=2, column=0, columnspan=5, sticky="we", pady=10, padx=10)

style.configure('TLabelframe', background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
style.configure('TRadiobutton', background=BACKGROUND_COLOR, foreground=FOREGROUND_COLOR)
style.map('TRadiobutton', background=[('active', BACKGROUND_COLOR)], foreground=[('active', ACCENT_COLOR)])

sort_best = ttk.Radiobutton(sort_frame, text='Best Match', variable=sort_var, value='')
sort_best.pack(side='left', padx=5)
sort_stars = ttk.Radiobutton(sort_frame, text='Most Stars', variable=sort_var, value='stars')
sort_stars.pack(side='left', padx=5)
sort_updated = ttk.Radiobutton(sort_frame, text='Latest Update', variable=sort_var, value='updated')
sort_updated.pack(side='left', padx=5)

# Create a text widget to display the results with a scrollbar
result_frame = ttk.Frame(content_frame)
result_frame.grid(row=1, column=0, columnspan=5, sticky='nsew', pady=(0, 10), padx=10)

result_text = tk.Text(result_frame, wrap="word", state="disabled", bg=BACKGROUND_COLOR, fg=FOREGROUND_COLOR, font=(FONT_FAMILY, FONT_SIZE))
result_text.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=result_text.yview)
scrollbar.pack(side='right', fill='y')
result_text['yscrollcommand'] = scrollbar.set

# Configure grid weights
content_frame.columnconfigure(1, weight=1)
content_frame.columnconfigure(3, weight=1)
content_frame.rowconfigure(1, weight=1)

# Start the main loop
window.mainloop()
