from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component, Scope


@Component
@Scope("prototype")
class D:
    def my_print(self):
        print(self)
