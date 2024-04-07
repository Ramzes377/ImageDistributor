from multiprocessing import set_start_method

from app.ui import App

if __name__ == '__main__':

    # init_worker()
    # set_start_method('spawn', True)

    app = App()
    app.mainloop()
