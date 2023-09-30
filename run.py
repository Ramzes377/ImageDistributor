import warnings

from app.ui import App

warnings.simplefilter('default')

if __name__ == '__main__':
    app = App()
    app.mainloop()
