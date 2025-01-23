import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from functools import lru_cache
from time import sleep
import time
from concurrent.futures import ThreadPoolExecutor
import math
from datetime import datetime
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from queue import Queue

# Font settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 11

# Theme settings
THEME_STYLE = "clam"
COLORS = {
    'bg': '#2b2b2b',
    'fg': '#ffffff',
    'button': '#404040',
    'button_hover': '#505050',
    'entry_bg': '#363636',
    'highlight': '#4a9eff'
}

# Configure session with connection pooling and retries
def create_github_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(
        pool_connections=5,
        pool_maxsize=20,
        max_retries=retry_strategy
    )
    session.mount("https://", adapter)
    return session

# Global session
github_session = create_github_session()

class SearchThread(threading.Thread):
    def __init__(self, query, sort_by, language_filter, page, callback):
        super().__init__()
        self.query = query
        self.sort_by = sort_by
        self.language_filter = language_filter
        self.page = page
        self.callback = callback
        self.daemon = True

    def run(self):
        try:
            result = cached_get_repositories(
                self.query,
                self.sort_by,
                self.language_filter,
                self.page,
                github_session
            )
            if self.callback:
                window.after(0, lambda: self.callback(result))
        except Exception as e:
            window.after(0, lambda: self.callback(None))

# Add caching for API requests
@lru_cache(maxsize=100)
def cached_get_repositories(query, sort_by, language_filter, page=1, session=None):
    session = session or github_session
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
            response = session.get(url, params=params, timeout=10)
            
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

class GitHubSearch:
    def __init__(self, result_text):
        self.page = 1
        self.loading = False
        self.has_more = True
        self.result_text = result_text
        self.current_query = ""
        self.current_sort = ""
        self.current_language = ""
        self.results_count = 0
        self.search_thread: Optional[SearchThread] = None
        self.result_queue = Queue()
        self.loading_label = None
        self.debounce_timer = None

    def reset_search(self):
        self.page = 1
        self.loading = False
        self.has_more = True
        self.results_count = 0

    def show_loading(self):
        if not self.loading_label:
            self.loading_label = ttk.Label(
                result_frame,
                text="Loading...",
                background=COLORS['bg'],
                foreground=COLORS['fg']
            )
            self.loading_label.place(relx=0.5, rely=0.5, anchor="center")

    def hide_loading(self):
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
        
    def format_date(self, date_str):
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        return date_obj.strftime('%B %d, %Y')

    def load_more_results(self):
        if self.loading or not self.has_more:
            return

        self.loading = True
        self.show_loading()

        def callback(repositories):
            self.loading = False
            self.hide_loading()
            if repositories and 'items' in repositories:
                self.add_results(repositories['items'])
                self.page += 1
                self.has_more = len(repositories['items']) == 30
            else:
                self.has_more = False

        self.search_thread = SearchThread(
            self.current_query,
            self.current_sort,
            self.current_language,
            self.page,
            callback
        )
        self.search_thread.start()

    def add_results(self, repositories):
        # Create all the text content first
        content = []
        for repo in repositories:
            try:
                repo_text = (
                    f'{"─" * 80}\n'
                    f'📦 {repo.get("name", "N/A")}\n\n'
                    f'📝 {repo.get("description", "No description provided.")}\n\n'
                    f'⭐ {repo.get("stargazers_count", 0):,}   '
                    f'👁 {repo.get("watchers", 0):,}   '
                    f'🔤 {repo.get("language", "Unknown")}\n'
                    f'👤 {repo.get("owner", {}).get("login", "Unknown")}   '
                    f'📅 {self.format_date(repo.get("created_at", "Unknown"))}\n\n'
                )
                content.append((repo_text, repo.get('html_url', '')))
            except Exception as e:
                print(f"Error processing repository: {e}")
                continue

        # Batch update the text widget
        self.result_text.config(state="normal")
        if self.page == 1:
            self.result_text.delete(1.0, tk.END)
            self.results_count = 0

        for text, url in content:
            self.result_text.insert(tk.END, text)
            if url:
                link_text = "🔗 View Repository\n\n"
                start = self.result_text.index("end-2c linestart")
                self.result_text.insert(tk.END, link_text)
                end = self.result_text.index("end-2c")
                tag_name = f'link_{self.results_count}'
                self.result_text.tag_add(tag_name, start, end)
                self.result_text.tag_config(tag_name, foreground="#4a9eff", underline=True)
                self.result_text.tag_bind(tag_name, '<Button-1>', 
                    lambda e, url=url: webbrowser.open_new_tab(url))
            self.results_count += 1

        self.result_text.config(state="disabled")

def perform_search(sort_by=None):
    query = entry.get()
    if not query.strip():
        messagebox.showwarning("Warning", "Please enter a search query")
        return
        
    language_filter = language_var.get()
    if language_filter == 'All':
        language_filter = ''
    
    github_search.current_query = query
    github_search.current_sort = sort_by
    github_search.current_language = language_filter
    github_search.reset_search()
    github_search.load_more_results()

def debounced_search(sort_by=None):
    if github_search.debounce_timer:
        window.after_cancel(github_search.debounce_timer)
    github_search.debounce_timer = window.after(300, lambda: perform_search(sort_by))

def on_scroll(event):
    if not github_search.loading and github_search.has_more:
        # Calculate if we're near the bottom
        first, last = result_text.yview()
        if last >= 0.9:  # Load more when 90% scrolled
            github_search.load_more_results()

# Create the main window
window = tk.Tk()
window.title('GitHub Repository Search')
window.geometry("1200x800")
window.configure(bg=COLORS['bg'])

# Create a style for the GUI elements
style = ttk.Style()
style.theme_use(THEME_STYLE)

# Configure styles
style.configure('TFrame', background=COLORS['bg'])
style.configure('TLabel', 
    background=COLORS['bg'], 
    foreground=COLORS['fg'], 
    font=(FONT_FAMILY, FONT_SIZE)
)
style.configure('TEntry', 
    fieldbackground=COLORS['entry_bg'], 
    foreground=COLORS['fg'], 
    font=(FONT_FAMILY, FONT_SIZE)
)
style.configure('TButton', 
    background=COLORS['button'],
    foreground=COLORS['fg'],
    font=(FONT_FAMILY, FONT_SIZE, "bold"),
    padding=(15, 8)
)
style.configure('Search.TButton',
    background=COLORS['highlight'],
    padding=(20, 8)
)
style.configure('TRadiobutton',
    background=COLORS['bg'],
    foreground=COLORS['fg'],
    font=(FONT_FAMILY, FONT_SIZE)
)
style.configure('TLabelframe',
    background=COLORS['bg'],
    foreground=COLORS['fg']
)
style.configure('TLabelframe.Label',
    background=COLORS['bg'],
    foreground=COLORS['fg'],
    font=(FONT_FAMILY, FONT_SIZE)
)

# Create hover effects
style.map('TButton',
    background=[('active', COLORS['button_hover'])],
    foreground=[('active', COLORS['fg'])]
)
style.map('Search.TButton',
    background=[('active', '#3a89e0')],
    foreground=[('active', COLORS['fg'])]
)

# Create a frame to hold the content
content_frame = ttk.Frame(window)
content_frame.pack(fill="both", expand=True, padx=30, pady=20)

# Create a search frame for better organization
search_frame = ttk.Frame(content_frame)
search_frame.pack(fill="x", pady=(0, 20))

# Update search components layout
label = ttk.Label(search_frame, text='Search GitHub Repositories:')
label.pack(anchor="w", pady=(0, 5))

search_input_frame = ttk.Frame(search_frame)
search_input_frame.pack(fill="x")

entry = ttk.Entry(search_input_frame)
entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

language_label = ttk.Label(search_input_frame, text='Language:')
language_label.pack(side="left", padx=(0, 5))

language_var = tk.StringVar()
language_combobox = ttk.Combobox(search_input_frame, textvariable=language_var, width=15)
language_combobox['values'] = ['All', 'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Ruby', 'Swift']
language_combobox.current(0)
language_combobox.pack(side="left", padx=(0, 10))

button = ttk.Button(search_input_frame, text='Search', command=lambda: perform_search(sort_var.get()), style='Search.TButton')
button.pack(side="right")

# Update sort options layout
sort_frame = ttk.LabelFrame(content_frame, text='Sort By')
sort_frame.pack(fill="x", pady=(0, 20))

sort_var = tk.StringVar(value='')
sort_best = ttk.Radiobutton(sort_frame, text='Best Match', variable=sort_var, value='')
sort_best.pack(side='left', padx=20, pady=10)
sort_stars = ttk.Radiobutton(sort_frame, text='Most Stars', variable=sort_var, value='stars')
sort_stars.pack(side='left', padx=20, pady=10)
sort_updated = ttk.Radiobutton(sort_frame, text='Latest Update', variable=sort_var, value='updated')
sort_updated.pack(side='left', padx=20, pady=10)

# Update results display
result_frame = ttk.Frame(content_frame)
result_frame.pack(fill="both", expand=True)

result_text = tk.Text(
    result_frame,
    wrap="word",
    state="disabled",
    font=(FONT_FAMILY, FONT_SIZE),
    bg=COLORS['entry_bg'],
    fg=COLORS['fg'],
    insertbackground=COLORS['fg'],
    selectbackground=COLORS['highlight'],
    selectforeground=COLORS['fg'],
    relief="flat",
    padx=10,
    pady=10
)
result_text.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=result_text.yview)
scrollbar.pack(side='right', fill='y')
result_text['yscrollcommand'] = scrollbar.set

# Bind enter key to search
entry.bind('<Return>', lambda event: perform_search(sort_var.get()))

# Update search binding to use debouncing
entry.bind('<KeyRelease>', lambda event: debounced_search(sort_var.get()))
button.configure(command=lambda: perform_search(sort_var.get()))

# Configure grid weights
content_frame.columnconfigure(1, weight=1)
content_frame.columnconfigure(3, weight=1)
content_frame.rowconfigure(1, weight=1)

# Initialize the GitHub search handler
github_search = GitHubSearch(result_text)

# Bind scroll event
result_text.bind('<MouseWheel>', on_scroll)
result_text.bind('<Button-4>', on_scroll)
result_text.bind('<Button-5>', on_scroll)

# Start the main loop
window.mainloop()
