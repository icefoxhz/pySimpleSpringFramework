import copy

from pySimpleSpringFramework.spring_core.util.commonUtils import is_instance


class AttributeAccessorSupport:
    def __init__(self):
        self._attributes = {}

    def set_attribute(self, name, value):
        self._attributes[name] = value

    def get_attribute(self, name) -> object:
        return self._attributes.get(name, None)

    def remove_attribute(self, name):
        if name is not None and name in self._attributes:
            self._attributes.pop(name)

    def has_attribute(self, name) -> bool:
        return name in self._attributes

    def attributeNames(self) -> list:
        return list(self._attributes.keys())

    def copy_attributes_from(self, source):
        if isinstance(source, AttributeAccessorSupport):
            d = {}
            for name in source.attributeNames():
                d[name] = copy.deepcopy(source.get_attribute(name))
            self._attributes.update(d)
