from tkinter import LabelFrame, Tk, PhotoImage, ttk
import os
import pickle


root = Tk()
root.title('Image distributor')
root.minsize(width=640, height=480)
s = ttk.Style()
s.theme_use('vista')


main_icon = "./icons/sorting.png"
settings_icon = ''

BASE_DIR = os.path.abspath('../')

CONFIG = {}
config_path = os.path.join(os.path.abspath('../'), '../.config')


try:
    with open(config_path, 'rb+') as f:
        unpickler = pickle.Unpickler(f)
        CONFIG = unpickler.load()
    if not os.path.isfile(config_path):
        CONFIG['last_directory'] = BASE_DIR
except (FileNotFoundError, EOFError):
    CONFIG = {'last_directory': BASE_DIR}
    with open(config_path, 'wb+') as f:
        pickle.dump(CONFIG, f)
    os.system("attrib +h .config")  # HIDE config file

CUR_DIR = CONFIG.get('last_directory', BASE_DIR)

def change_state(e):
    CONFIG[type(root).__name__] = root.winfo_geometry(), root.state()
root.bind('<Configure>', change_state)


def rewrite_config(**params):
    new_config = {**CONFIG, **params}
    with open(config_path, 'rb+') as f:
        pickle.dump(new_config, f)

def save_config():
    with open(os.path.join(os.path.abspath('../'), '../.config'), 'rb+') as f:
        pickle.dump(CONFIG, f)


try:
    geometry, state = CONFIG[type(root).__name__]
    if state == 'zoomed':
        root.state('zoomed')
    else:
        root.geometry(geometry)
except KeyError:
    pass


def get_frame(text, root_widget = None, pack_args = {}, **kwargs):
    kw = {'bg': '#1f1f22', 'fg':'white', 'padx': 10, 'pady': 5, 'bd': 0}
    if root_widget:
        widget = LabelFrame(root_widget, text = text, **{**kw, **kwargs})
    else:
        widget = LabelFrame(text=text, **{**kw, **kwargs})
    pa = {'side': 'right', 'fill':'both', 'expand': 0}
    widget.pack(**{**pa, **pack_args})
    return widget


IMAGE_FORMATS = ['jpg', 'png', 'jpeg', 'bmp', 'gif']

def file_is_image(filename):
    try:
        name, format = filename.split('.')
    except ValueError:
        return False
    return any([format == suffix for suffix in IMAGE_FORMATS])



try:
    root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=main_icon)) #set window ICON
except:
    pass


