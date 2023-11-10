from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired, Value


@Component
class A:
    @Value({"spring.profiles.include": "v1"})
    def __init__(self):
        self.d = None
        self.v1 = None
        self._url = None
        self.b = None
        self.__name = "zhangsan"

    def before_init(self):
        print("a  before_init")

    def after_init(self):
        print("a  after_init")

    @Autowired
    def set_params(self, b, d):
        self.b = b
        self.d = d

    def my_print(self):
        print("this is a!  v1 = {}, b = {}, d= {}".format(self.v1, self.b, self.d))

    def f1(self):
        print("this is a's f1")
        print()
