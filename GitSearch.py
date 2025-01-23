import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from functools import lru_cache
from time import sleep
import time
from concurrent.futures import ThreadPoolExecutor

# Font settings
FONT_FAMILY = "Helvetica"
FONT_SIZE = 12

# Theme settings
THEME_STYLE = "clam"

# Add caching for API requests
@lru_cache(maxsize=100)
def cached_get_repositories(query, sort_by, language_filter, page=1):
    url = 'https://api.github.com/search/repositories'
    q = query
    if language_filter:
        q += f' language:{language_filter}'
    params = {
        'q': q,
        'sort': sort_by if sort_by else 'best match',
        'order': 'desc',
        'page': page,
        'per_page': 30
    }

    # Add retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Handle rate limiting
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = min(reset_time - time.time(), 60)
                if wait_time > 0:
                    sleep(wait_time)
                continue
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return None
            sleep(2 ** attempt)  # Exponential backoff

def batch_update_results(result_text, repositories):
    result_text.config(state="normal")
    result_text.delete(1.0, tk.END)
    
    # Prepare all text content first
    content = []
    for i, repo in enumerate(repositories):
        try:
            repo_text = (
                f'Title: {repo.get("name", "N/A")}\n'
                f'Description: {repo.get("description", "No description provided.")}\n'
                f'Stars: {repo.get("stargazers_count", 0)}\n'
                f'Language: {repo.get("language", "Unknown")}\n'
                f'Owner: {repo.get("owner", {}).get("login", "Unknown")}\n'
                f'Created at: {repo.get("created_at", "Unknown")}\n'
                f'Watchers: {repo.get("watchers", 0)}\n\n'
            )
            content.append((repo_text, repo.get('html_url', '')))
        except Exception as e:
            print(f"Error processing repository: {e}")
            continue

    # Batch insert all content
    for i, (text, url) in enumerate(content):
        result_text.insert(tk.END, text)
        if url:  # Only create link if URL exists
            tag_name = f'link_{i}'
            start_idx = f"{float(i*8 + 1)}"  # Account for multi-line entries
            end_idx = f"{float(i*8 + 1)} lineend"
            result_text.tag_add(tag_name, start_idx, end_idx)
            result_text.tag_config(tag_name, foreground="blue", underline=True)
            result_text.tag_bind(tag_name, '<Button-1>', lambda e, url=url: webbrowser.open_new_tab(url))

    result_text.config(state="disabled")

def perform_search(sort_by=None):
    query = entry.get()
    if not query.strip():
        messagebox.showwarning("Warning", "Please enter a search query")
        return
        
    language_filter = language_var.get()
    
    # Use ThreadPoolExecutor for async loading
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(cached_get_repositories, query, sort_by, language_filter)
        try:
            repositories = future.result(timeout=15)
            if repositories and 'items' in repositories:
                batch_update_results(result_text, repositories['items'])
            else:
                result_text.config(state="normal")
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, 'No repositories found for the given query.')
                result_text.config(state="disabled")
        except Exception as e:
            result_text.config(state="normal")
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, f'An error occurred: {str(e)}')
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
