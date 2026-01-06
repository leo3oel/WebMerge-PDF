import PyPDF2
from datetime import datetime
from pathlib import Path
from flask import url_for

class PDF:
    filepath: Path
    static_path: Path
    filename: str
    filesize: int
    filesize_str: str | None = None
    timestamp: datetime | None
    timestamp_str: str | None = None
    url: str | None = None
    num_pages: int = 0

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.static_path = f'input/{filepath.name}'  # relative to static folder

        # populate metadata
        self._populate_file_metadata()

        # page count (keeps existing behaviour)
        self.num_pages: int = self._get_num_pages()

    def _populate_file_metadata(self) -> None:
        """
        Fill filename, filesize and timestamp of last modification.
        """
        self.filename = self.filepath.name  # ensure Path object
        self.filesize = self._get_filesize()
        self.timestamp = self._get_mtime()
        self.timestamp_str = self.timestamp.strftime("%H:%M:%S %d.%m.%Y") if self.timestamp else "unknown"
        self.filesize_str = self.human_readable_size(self.filesize)

    def set_url(self):
        self.url = url_for('static', filename=self.static_path)
    
    def _get_filesize(self) -> int:
        try:
            return int(self.filepath.stat().st_size)
        except Exception:
            return 0

    def _get_mtime(self) -> datetime | None:
        try:
            ts = self.filepath.stat().st_mtime
            return datetime.fromtimestamp(ts)
        except Exception:
            return None

    def _get_num_pages(self) -> int:
        try:
            with open(self.filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception:
            return 0

    def __repr__(self):
        return f"PDF({self.filepath.name})"
    
    def rotate_cw(self):
        self.rotate(90)

    def rotate_ccw(self):
        self.rotate(-90)

    def rotate(self, degrees=90):
        with open(self.filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            writer = PyPDF2.PdfWriter()
            for page in reader.pages:
                page.rotate(degrees)
                writer.add_page(page)
            with open(self.filepath, "wb") as out_f:
                writer.write(out_f)
        # update metadata since file changed
        self._populate_file_metadata()
    
    def split(self) -> list[Path]:
        """
        Splits the PDF into individual pages and returns list of new file paths.
        """
        new_filepaths = []
        with open(self.filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                new_filename = self.filepath.stem + f"_page_{i+1}" + self.filepath.suffix
                new_filepath = self.filepath.parent / new_filename
                with open(new_filepath, "wb") as out_f:
                    writer.write(out_f)
                new_filepaths.append(new_filepath)
        return new_filepaths

    def human_readable_size(self, num: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return f"{num:3.1f} {unit}"
            num /= 1024.0
        return f"{num:.1f} PB"
