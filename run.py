import warnings

from app.ui.app import App

warnings.simplefilter('default')

if __name__ == '__main__':
    app = App()
    app.mainloop()
