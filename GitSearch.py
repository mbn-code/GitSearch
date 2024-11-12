import tkinter as tk
from tkinter import ttk
import webbrowser
import requests

# Font settings
FONT_FAMILY = "Helvetica"
FONT_SIZE = 12

# Theme settings
THEME_STYLE = "clam"

def get_repositories(query, sort_by, language_filter):
    url = 'https://api.github.com/search/repositories'
    q = query
    if language_filter:
        q += f' language:{language_filter}'
    params = {
        'q': q,
        'sort': sort_by if sort_by else 'best match',
        'order': 'desc'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

    if response.status_code == 200 and 'items' in data:
        repositories = []
        items = data['items']
        if not items:
            return []
        for item in items:
            repository = {
                'title': item.get('name', 'N/A'),
                'html_url': item.get('html_url', ''),
                'description': item.get('description', 'No description provided.'),
                'stars': item.get('stargazers_count', 0),
                'language': item.get('language', 'Unknown'),
                'owner': item.get('owner', {}).get('login', 'Unknown'),
                'created_at': item.get('created_at', 'Unknown'),
                'forks': item.get('forks', 0),
                'watchers': item.get('watchers', 0)
            }
            repositories.append(repository)
        return repositories
    else:
        return []

def perform_search(sort_by=None):
    query = entry.get()
    language_filter = language_var.get()
    repositories = get_repositories(query, sort_by, language_filter)
    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)
    if repositories:
        for i, repository in enumerate(repositories):
            title = repository['title']
            html_url = repository['html_url']
            description = repository['description']
            stars = repository['stars']
            language = repository['language']
            owner = repository['owner']
            created_at = repository['created_at']
            watchers = repository['watchers']

            result_text.insert(tk.END, f'Title: {title}\n')
            result_text.insert(tk.END, f'Description: {description}\n')
            result_text.insert(tk.END, f'Stars: {stars}\n')
            result_text.insert(tk.END, f'Language: {language}\n')
            result_text.insert(tk.END, f'Owner: {owner}\n')
            result_text.insert(tk.END, f'Created at: {created_at}\n')
            result_text.insert(tk.END, f'Watchers: {watchers}\n')

            tag_name = f'link_{i}'
            result_text.tag_bind(tag_name, '<Button-1>', lambda _event, url=html_url: webbrowser.open_new_tab(url))
            result_text.tag_config(tag_name, foreground="blue", underline=True)
            result_text.tag_bind(tag_name, '<Button-1>', lambda event, url=html_url: webbrowser.open_new_tab(url))
    else:
        result_text.insert(tk.END, 'No repositories found for the given query.')
    result_text.config(state="disabled")

# Create the main window
window = tk.Tk()
window.title('GitHub Search')

# Configure the window size and position
window.geometry("1000x700")
window.resizable(True, True)

# Create a style for the GUI elements
style = ttk.Style()
style.theme_use(THEME_STYLE)
style.configure('TLabel', font=(FONT_FAMILY, FONT_SIZE))
style.configure('TEntry', font=(FONT_FAMILY, FONT_SIZE))
style.configure('TButton', font=(FONT_FAMILY, FONT_SIZE, "bold"))
style.configure('TText', font=(FONT_FAMILY, FONT_SIZE))
style.configure('TCombobox', font=(FONT_FAMILY, FONT_SIZE))

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
language_combobox = ttk.Combobox(content_frame, textvariable=language_var)
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

sort_best = ttk.Radiobutton(sort_frame, text='Best Match', variable=sort_var, value='')
sort_best.pack(side='left', padx=5)
sort_stars = ttk.Radiobutton(sort_frame, text='Most Stars', variable=sort_var, value='stars')
sort_stars.pack(side='left', padx=5)
sort_updated = ttk.Radiobutton(sort_frame, text='Latest Update', variable=sort_var, value='updated')
sort_updated.pack(side='left', padx=5)

# Create a text widget to display the results with a scrollbar
result_frame = ttk.Frame(content_frame)
result_frame.grid(row=1, column=0, columnspan=5, sticky='nsew', pady=(0, 10), padx=10)

result_text = tk.Text(result_frame, wrap="word", state="disabled", font=(FONT_FAMILY, FONT_SIZE))
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
