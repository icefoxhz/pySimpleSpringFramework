from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired


class DsParent:
    def __init__(self):
        self._dsTest = None
        self._mapping = None

    @Autowired
    def set_params(self, mapping, dsTest):
        self._mapping = mapping
        self._dsTest = dsTest
