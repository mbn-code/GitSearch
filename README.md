# GitSearch

This script is a Python program that utilizes the Tkinter library to create a graphical user interface (GUI) for searching GitHub repositories based on a user's query. It retrieves repository data from the GitHub API, displays the results in a text widget, and allows the user to open a repository's URL in a web browser.

## Dependencies

The script requires the following dependencies:

- Python 3.x
- `tkinter` library
- `requests` library

## Installation

1. Clone the repository or download the script file.
2. Install the required dependencies by running the following command:

```shell
pip install requests
```

## Usage

1. Run the script using the following command:

```shell
python script.py
1. Run the script using the following command:

```shell
python script.py
```

2. The program will open a window with a search input field.

3. Enter your search query and click the "Search" button.

4. The program will retrieve the repositories matching the query and display the results in the text widget.

5. Click on the "Open in Browser" link for any repository to open its URL in a web browser.
The script provides some customization options:

- **Font settings**: You can modify the `FONT_FAMILY` and `FONT_SIZE` variables to change the font used in the GUI.
- **Color settings**: You can modify the `PRIMARY_COLOR`, `SECONDARY_COLOR`, and `LINK_COLOR` variables to change the colors used in the GUI.

## License

This script is licensed under the [MIT License](LICENSE).
