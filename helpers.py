import json
from os.path import join, dirname, abspath, exists

class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class _Config(metaclass=_Singleton):
    _root_path = dirname(abspath(__file__))
    _templates_folder_path = join(_root_path, 'templates')
    _resources_folder_path = join(_root_path, 'resources')
    @property
    def __templates(self): return self._templates_folder_path
    @__templates.getter
    def template_folder_path(self): return self.__templates
    @property
    def __resources(self): return self._resources_folder_path
    @__resources.getter
    def resources_folder_path(self): return self.__resources

    def get_resource(self, resource):
        data = {}
        try:
            with open(join(self.resources_folder_path, resource)) as fp:
                data = json.load(fp)
        except Exception:
            return False
        return data

config = _Config()
singleton = _Singleton
