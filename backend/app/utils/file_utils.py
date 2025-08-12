# For later use (to keep file-related helper functions separate):

# sanitize_filename(filename: str) -> str
# To prevent unsafe characters (../ or OS-specific issues).

# save_temp_file(file: UploadFile) -> str
# So the “save to temp” logic is reusable.

# download_file_from_drive(url: str) -> str
# For later Sanity Studio automation.

# delete_file(file_path: str)
# As a cleaner abstraction than calling os.remove() directly everywhere.
