from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired


@Component
class ServiceA:
    def __init__(self):
        self._c = None

    @Autowired
    def set_params(self, c):
        self._c = c

    def callback_function(self, future):
        result = future.result()
        print(f"Callback function: Result is {result}")

    def print(self):
        print(self._c.name)
        return self._c.name
