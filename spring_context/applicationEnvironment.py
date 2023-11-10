from pySimpleSpringFramework.spring_core.util.commonUtils import get_nested_value


class ApplicationEnvironment:
    def __init__(self):
        self.__env = {}

    def set_env(self, env):
        self.__env = env

    def get(self, key, raise_ex=True) -> any:
        return get_nested_value(key, self.__env, raise_ex)

    def get_all(self) -> dict:
        return self.__env
