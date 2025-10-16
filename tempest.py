import os


def strip_extension(filename):
    """
    Strips the extension from a filename.

    Args:
        filename (str): The input filename (e.g., "my_document.txt", "archive.tar.gz").

    Returns:
        str: The filename without its extension.
    """
    base_name, extension = os.path.splitext(filename)
    return base_name


# --- Examples ---
print(f"File with single extension: {strip_extension('my_document.txt')}")
print(f"File with multiple extensions: {strip_extension('archive.tar.gz')}")
print(f"File with no extension: {strip_extension('config_file')}")
print(f"File with leading dot (hidden file on Unix-like systems): {strip_extension('.bashrc')}")
print(f"File with only a dot: {strip_extension('.env')}")
print(f"File with only a dot at the end: {strip_extension('report.')}")
print(f"Empty string: {strip_extension('')}")
print(f"Just a dot: {strip_extension('.')}")
print(f"Just two dots: {strip_extension('..')}")
print(f"Path with extension: {strip_extension('/home/user/documents/report.pdf')}")
print(f"Windows path with extension: {strip_extension('C:\\Users\\JohnDoe\\Desktop\\image.jpg')}")
