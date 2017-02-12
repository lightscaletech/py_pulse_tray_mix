from os import path
import configparser


CONTEXT_APPLICATION = 'Apps'
CONTEXT_DEVICE      = 'Devices'
CONTEXT_ACTION      = 'Actions'


sys_icon_path = '/usr/share/icons/'
usr_icon_path = '~/.icons/'

class Icon(object):
    pass

class GtkIconTheme(object):

    inherits = None
    directories = []

    class Directory(object):
        def __init__(self, config, name):
            self.uri = name
            self.context = config.get(name, 'Context')
            self.size = config.get(name, 'Size')

    def __init__(self, name, fallback, context=None):
        self.path = self.find_theme(name)
        config = configparser.ConfigParser()
        config.read(path)
        inherits = config.get('Icon Theme', 'Inherits')
        if inherits is not None:
            self.inherits = GtkIconTheme(inherits, fallback, context)
        elif fallback is not None:
            self.inherits = GtkIconTheme(fallback, None, context)

    def load_directories(self, config, context):
        dstr = config.get('Icon Theme', 'Directories')
        dlist = dstr.split(',')
        for d in dlist:
            direc = Directory(config, d)
            if direc.context in context: self.directories.append(direc)
            elif context is None: self.directories.append(direc)

    def try_dir(self, path):
        return path.isdir(path)

    def find_theme(self, name):
        path = usr_icon_path + name
        if try_dir(path): return path
        path = sys_icon_path + name
        if try_dir(path): return path

class IconFinder(object):

    gtk3_setting = '~/.config/gtk-3.0/settings.ini'

    def __init__(self):
        self.theme_name = self.get_current_theme()
        self.theme = GtkIconTheme(self.theme_name, 'hicolor',
                                  [CONTEXT_APPLICATION, CONTEXT_DEVICE])

    def get_current_theme(self):
        settings = configparser.ConfigParser()
        settings.read(self.gtk3_setting)
        settings.get('Settings', 'gtk-icon-theme-name')

    def walk_icon_folder(self, path, name):
        pass

    def walk_icon_sizes(self, path, name):
        pass

    def walk_icon_themes(self):
        pass

    def find_icon(self, type, name):
        pass
