from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired


@Component
class C:
    def __init__(self):
        self.name = "zs"
        self.c = None
        self.a = None

    @Autowired
    def set_params(self, a, c):
        self.a = a
        self.c = c

    def my_print(self):
        print("this is c, c = {}, a = {}".format(self.c, self.a))
