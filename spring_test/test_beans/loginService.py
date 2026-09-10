from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component


@Component
class LoginService:
    def __init__(self):
        self.name = "loginService"
