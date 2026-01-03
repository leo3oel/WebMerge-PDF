from dataclasses import dataclass

@dataclass
class SavePath:
    name: str
    description: str


class Config:
    """
    ToDo: Read config from file or smthn
    """
    save_paths: list[SavePath] = [
        SavePath(name="test", description="Test Output Folder"),
        SavePath(name="output", description="Main Output Folder"),
        SavePath(name="final", description="Final Versions Folder")]
    selected_save_path: SavePath | None = None

    def __init__(self):
        pass

    def set_save_path(self, path_name: str):
        for sp in self.save_paths:
            if sp.name == path_name:
                self.selected_save_path = sp
                return
        self.selected_save_path = None
