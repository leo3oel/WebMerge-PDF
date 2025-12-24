from pathlib import Path
import PyPDF2

class PDF:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.num_pages = self._get_num_pages()

    def _get_num_pages(self) -> int:
        with open(self.filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages)

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
        # TODO: also delete from filesystem
    
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


if __name__ == "__main__":
    path = Path.cwd() / "static"
    pdf_editor = PdfEditor(path)
    pdf_editor.create_pdf_list()
    print(pdf_editor.get_ordered_filepaths())