import customtkinter

from app.api import container
from app.ui.main.bottom.frame import DistributeButtonsFrame
from app.ui.main.top.frame import TopFrame
from app.ui.menu import AppMenu


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.geometry("640x480")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        DistributeButtonsFrame(self)
        TopFrame(self)

        self.configure(menu=AppMenu(self))
        self.title('Image distributor')

    def destroy(self):
        super().quit()

    def change_directory(self, path: str) -> None:
        container.directory = path
        container.save()

        for name, children in self.children.items():
            if name == '!appmenu':
                continue

            children.change_directory(path) # noqa



