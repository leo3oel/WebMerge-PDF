from pathlib import Path
import os
from PyPDF2 import PdfWriter, PdfReader
from flask import url_for

from Pdf import PDF

class PdfEditor:
    _working_dir: Path
    _pdf_files: list[PDF]

    def __init__(self, path: Path):
        self._working_dir = path
        self._pdf_files = []

    def create_pdf_list(self):
        self._pdf_files = []
        for file in sorted(self._working_dir.iterdir()):
            if file.suffix.lower() == ".pdf":
                self._pdf_files.append(PDF(file))

    def get_pdf_files(self) -> list[PDF]:
        return self._pdf_files

    def get_ordered_filepaths(self) -> list[str]:
        """
        Returns the filenames (relative paths) in current order.
        """
        return [pdf.filepath.name for pdf in self._pdf_files]

    def _find_index(self, pdf_filename: str) -> int | None:
        for i, pdf in enumerate(self._pdf_files):
            if pdf.filepath.name == pdf_filename:
                return i
        return None

    def move_file_up(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is None or idx == 0:
            return  # can't move
        # swap with previous
        self._pdf_files[idx - 1], self._pdf_files[idx] = self._pdf_files[idx], self._pdf_files[idx - 1]

    def move_file_down(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is None or idx == len(self._pdf_files) - 1:
            return  # can't move
        # swap with next
        self._pdf_files[idx], self._pdf_files[idx + 1] = self._pdf_files[idx + 1], self._pdf_files[idx]

    def delete_file(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is not None:
            del self._pdf_files[idx]
        os.remove(self._working_dir / pdf_filename)
    
    def rotate_file_cw(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is not None:
            self._pdf_files[idx].rotate_cw()

    def rotate_file_ccw(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is not None:
            self._pdf_files[idx].rotate_ccw()
        
    def split_pdf(self, pdf_filename: str):
        idx = self._find_index(pdf_filename)
        if idx is None:
            return
        pdf = self._pdf_files[idx]
        pdf_filepaths = pdf.split()
        for filepath in pdf_filepaths:
            self._pdf_files.insert(idx, PDF(filepath))
            idx += 1
        # After splitting, remove the original PDF from the list
        # ToDo: Also delete from filesystem
        del self._pdf_files[idx]

    def select_files(self, filenames: list[str]):
        self._pdf_files = [pdf for pdf in self._pdf_files if pdf.filepath.name in filenames]

    def set_urls(self):
        for pdf in self._pdf_files:
            pdf.set_url()
    
    def create_merged_pdf(self, output_filepath: Path):
        writer = PdfWriter()
        for pdf in self._pdf_files:
            reader = PdfReader(str(pdf.filepath))
            for page in reader.pages:
                writer.add_page(page)
        with open(output_filepath, "wb") as out_f:
            writer.write(out_f)

    def create_preview(self) -> str:
        preview_filepath = self._working_dir / "preview" / "preview.pdf"
        self.create_merged_pdf(preview_filepath)
        return url_for('static', filename='preview/preview.pdf')

    def delete_preview(self):
        preview_filepath = self._working_dir / "preview" / "preview.pdf"
        if preview_filepath.exists():
            os.remove(preview_filepath)

if __name__ == "__main__":
    path = Path.cwd() / "static"
    pdf_editor = PdfEditor(path)
    pdf_editor.create_pdf_list()
    print(pdf_editor.get_ordered_filepaths())