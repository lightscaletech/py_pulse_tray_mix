from os import path
import configparser


CONTEXT_APPLICATION = 'Apps'
CONTEXT_DEVICE      = 'Devices'
CONTEXT_ACTION      = 'Actions'

home_dir = path.expanduser('~')
sys_icon_path = '/usr/share/icons/'
usr_icon_path = home_dir + '/.icons/'

class Icon(object):
    pass

class GtkIconTheme(object):

    inherits = None
    directories = []

    class Directory(object):
        def __init__(self, config, name):
            self.uri = name
            self.context = config.get(name, 'Context')
            self.size = config.getint(name, 'Size')


    def __init__(self, name, context=None):
        self.path = self.find_theme(name)
        config = configparser.ConfigParser()
        config.read(self.path + '/index.theme')
        inherits = config.get('Icon Theme', 'Inherits')
        if inherits is not None: self.inherits = inherits.split(',')

        self.load_directories(config, context)

    def load_directories(self, config, context):
        dstr = config.get('Icon Theme', 'Directories')
        dlist = dstr.split(',')
        for d in dlist:
            direc = Directory(config, d)
            if direc.context in context: self.directories.append(direc)
            elif context is None: self.directories.append(direc)

        self.directories.sort(key = lambda d: d.size)

    def try_dir(self, p):
        return path.isdir(p)

    def find_theme(self, name):
        p = usr_icon_path + name
        if self.try_dir(p): return p
        p = sys_icon_path + name
        if self.try_dir(p): return p
        print (p)

class IconFinder(object):

    gtk3_setting = home_dir + '/.config/gtk-3.0/settings.ini'

    themes = []

    def __init__(self, context=None):
        self.theme_name = self.get_current_theme()


    def load_theme(self, name, context):
        pass


    def get_current_theme(self):
        settings = configparser.ConfigParser()
        settings.read(self.gtk3_setting)
        return settings.get('Settings', 'gtk-icon-theme-name')

    def walk_icon_folder(self, path, name):
        pass

    def walk_icon_sizes(self, path, name):
        pass

    def walk_icon_themes(self):
        pass

    def find_icon(self, type, name):
        pass
