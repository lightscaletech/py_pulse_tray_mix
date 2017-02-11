from os import path

class Icon(object):
    pass

class IconFinder(object):
    pixmap_path = '/usr/share/pixmaps'
    icon_path = '/usr/share/icon'

    theme_priority = 'hicolor'
    default_size = 256

    @staticmethod
    def int_to_folder(size):
        return "%ix%i" % (size, size)

    def walk_icon_sizes(self, path, name):
        pass

    def walk_icon_folder(self, path, name):
        pass

    def walk_icon_themes(self):
        pass
