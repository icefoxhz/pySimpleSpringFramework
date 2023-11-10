from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


def Aspect(cls):
    aspect_attr = AnnotationType.get_annotation_attr(AnnotationName.ASPECT)
    setattr(cls, aspect_attr, True)
    return cls

