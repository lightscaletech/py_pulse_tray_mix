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

class ThemeNotFound(Exception):
    pass

class GtkIconTheme(object):

    inherits = None
    directories = []

    class Directory(object):
        def __init__(self, config, name):
            self.uri = name
            self.context = config.get(name, 'Context')
            self.size = config.getint(name, 'Size')
            self.type = config.get(name, 'Type')

        def __repr__(self):
            return 'GtkIconTheme.Directory<uri=%s>' % self.uri

    def __init__(self, name, context=None):
        self.name = name
        self.path = self.find_theme(self.name)
        if self.path is None: raise ThemeNotFound()
        config = configparser.ConfigParser()
        config.read(self.path + '/index.theme')

        if config.has_option('Icon Theme', 'Inherits'):
            self.inherits = config.get('Icon Theme', 'Inherits').split(',')

        self.load_directories(config, context)

    def __repr__(self):
        return 'GtkIconTheme<name=%s>' % self.name
    def __str__(self):
        return self.name

    def load_directories(self, config, context):
        dstr = config.get('Icon Theme', 'Directories')
        dlist = dstr.split(',')
        for d in dlist:
            direc = self.Directory(config, d)
            if direc.context in context: self.directories.append(direc)
            elif context is None: self.directories.append(direc)

        self.directories.sort(key = lambda d: d.size, reverse=True)

    def try_dir(self, p):
        return path.isdir(p)

    def find_theme(self, name):
        p = usr_icon_path + name
        if self.try_dir(p): return p
        p = sys_icon_path + name
        if self.try_dir(p): return p

    def find_icon(self, ctx, name):
        print(self.name)
        print(self.directories)
        dirs = [d for d in self.directories
                if d.context == ctx and d.type != 'scalable']

class IconFinder(object):

    gtk3_setting = home_dir + '/.config/gtk-3.0/settings.ini'

    themes = []

    def __init__(self, context=None):
        self.theme_name = self.get_current_theme()
        self.load_theme(self.theme_name, context)

    def load_theme(self, name, context):
        try:
            theme = GtkIconTheme(name, context)
            self.themes.append(theme)

            if theme.inherits is not None:
                for n in theme.inherits:
                    self.load_theme(n, context)

        except ThemeNotFound as err: pass

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

    def find_icon(self, ctx, name):
        self.themes[0].find_icon(ctx, name)
