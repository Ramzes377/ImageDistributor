import customtkinter

from app.ui.main.bottom.frame import DistributeButtonsFrame
from app.ui.main.top.listbox import FileList
from app.ui.main.top.display import ImageFrame


class TopFrame(customtkinter.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        img_frame = ImageFrame(master=self)
        img_frame.pack(fill='both', expand=1, padx=5, pady=5, side='left')

        filelist = FileList(master=self,  copy_container=set(),
                            update=img_frame.change_image)
        filelist.pack(side='right', fill='y', expand=0)

        bot: DistributeButtonsFrame = master.children['!distributebuttonsframe']
        bot.select_next = filelist.select_next

        self.pack(side='top', fill='both', expand=1, padx=10, pady=10)

    def change_directory(self, path: str):
        filelist: FileList = self.children['!filelist']
        filelist.change_directory()
