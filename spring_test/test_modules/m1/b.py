from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired


@Component
class B:
    def __init__(self):
        self.c = None
        self.a = None

    @Autowired
    def set_params(self, a, c):
        self.a = a
        self.c = c

    def my_print(self):
        print("call b' my_print, a = {}, c = {}".format(self.a, self.c))

    def f1(self):
        print("call b' f1")

    def get_result(self):
        result = 1
        print("call b's get_result")
        return result
