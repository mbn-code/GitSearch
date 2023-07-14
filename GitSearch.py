import tkinter as tk
from tkinter import ttk
import webbrowser
import requests

# Font settings
FONT_FAMILY = "Helvetica"
FONT_SIZE = 12

# Color settings
PRIMARY_COLOR = "#2196f3"  # Material Blue 500
SECONDARY_COLOR = "#f5f5f5"  # Light Gray
LINK_COLOR = "#1e88e5"  # Material Blue 600

def get_repositories(query):
    url = 'https://api.github.com/search/repositories'
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        repositories = []
        items = data['items']
        for item in items:
            repository = {
                'title': item['name'],
                'html_url': item['html_url'],
                'description': item['description'],
                'stars': item['stargazers_count'],
                'language': item['language'],
                'owner': item['owner']['login'],
                'created_at': item['created_at'],
                'forks': item['forks'],
                'watchers': item['watchers']
            }
            repositories.append(repository)
        
        repositories = sorted(repositories, key=lambda x: x['stars'], reverse=True)
        return repositories
    else:
        return None

def perform_search():
    query = entry.get()
    repositories = get_repositories(query)
    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)
    if repositories:
        result_text.insert(tk.END, 'Repositories based on your search:\n\n')
        for repository in repositories:
            title = repository['title']
            html_url = repository['html_url']
            description = repository['description']
            stars = repository['stars']
            language = repository['language']
            owner = repository['owner']
            created_at = repository['created_at']
            forks = repository['forks']
            watchers = repository['watchers']

            result_text.insert(tk.END, f'Title: {title}\n')
            result_text.insert(tk.END, f'Description: {description}\n')
            result_text.insert(tk.END, f'Stars: {stars}\n')
            result_text.insert(tk.END, f'Language: {language}\n')
            result_text.insert(tk.END, f'Owner: {owner}\n')
            result_text.insert(tk.END, f'Created at: {created_at}\n')
            result_text.insert(tk.END, f'Forks: {forks}\n')
            result_text.insert(tk.END, f'Watchers: {watchers}\n')

            label = tk.Label(result_text, text='Open in Browser', fg=LINK_COLOR, cursor="hand2", font=(FONT_FAMILY, FONT_SIZE, "bold"))
            label.bind("<Button-1>", lambda event, url=html_url: webbrowser.open_new_tab(url))
            result_text.window_create(tk.END, window=label)
            result_text.insert(tk.END, '\n\n')
    else:
        result_text.insert(tk.END, 'No repositories found for the given query.')
    result_text.config(state="disabled")

# Create the main window
window = tk.Tk()
window.title('GitHub Search')

# Configure the window size and position
window.geometry("800x600")
window.resizable(False, False)

# Create a style for the GUI elements
style = ttk.Style()
style.configure('TLabel', background=SECONDARY_COLOR, foreground=PRIMARY_COLOR, font=(FONT_FAMILY, FONT_SIZE))
style.configure('TEntry', background="white", font=(FONT_FAMILY, FONT_SIZE))
style.configure('TButton', background=PRIMARY_COLOR, foreground="white", font=(FONT_FAMILY, FONT_SIZE, "bold"))
style.configure('TText', background=SECONDARY_COLOR, foreground="black", font=(FONT_FAMILY, FONT_SIZE))

# Create a frame to hold the content
content_frame = ttk.Frame(window, padding=20)
content_frame.pack(fill="both", expand=True)

# Create a label and entry for the search query
label = ttk.Label(content_frame, text='Enter a search query:')
label.grid(row=0, column=0, sticky="w", pady=10, padx=10)

entry = ttk.Entry(content_frame)
entry.grid(row=0, column=1, sticky="we", pady=10, padx=10)

# Create a button to perform the search
button = ttk.Button(content_frame, text='Search', command=perform_search)
button.grid(row=0, column=2, sticky="e", pady=10, padx=10)

# Create a text widget to display the results
result_text = tk.Text(content_frame, wrap="word", state="disabled", font=(FONT_FAMILY, FONT_SIZE))
result_text.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 10), padx=10)

# Configure grid weights
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=1)
content_frame.columnconfigure(2, weight=0)
content_frame.rowconfigure(1, weight=1)

# Start the main loop
window.mainloop()
