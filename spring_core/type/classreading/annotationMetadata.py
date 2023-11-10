from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType


class AnnotationMetadata:
    """
    描述类的装饰器元数据信息
    每个类对应一个 SimpleAnnotationMetadata
    """

    def __init__(self, cls):
        self.cls = cls
        """
        类上装饰器 和 对应的值
        {
            AnnotationName.SINGLETON : True,
            annotation_name2: value2,
            ...
        }
        
        """
        self._class_annotations = {}

        """
        方法 和 装饰器及对应的值
        {
            method1: {
                annotation_name: value,
                AnnotationName.AUTOWIRED : True,
                ...
            },
            method2: {
                annotation_name: value,
                AnnotationName.AUTOWIRED : True
                ...
            }
        }
        """
        self._annotated_methods = {}

    def get_methods(self, annotation_name) -> dict:
        methods = {}
        for method, annotate_dict in self._annotated_methods.items():
            for name, value in annotate_dict.items():
                if name == annotation_name:
                    methods[method] = value
        return methods

    def get_class_annotation(self, annotation_name):
        return self._class_annotations.get(annotation_name, None)

    def add_method_annotation(self, method, annotation_name, annotation_value):
        self._annotated_methods[method] = {
            annotation_name: annotation_value
        }

    def add_class_annotation(self, annotation_name, annotation_value):
        self._class_annotations[annotation_name] = annotation_value

    @staticmethod
    def introspect(bean_metadata):
        cls = bean_metadata.cls
        annotationMetadata = AnnotationMetadata(cls)

        # 获取类上的注解
        for annotation_name, annotation_attr in AnnotationType.types.items():
            if hasattr(cls, annotation_attr):
                annotationMetadata.add_class_annotation(annotation_name, getattr(cls, annotation_attr))

        # 获取方法上的注解
        methods = bean_metadata.get_methods()
        for method in methods:
            for annotation_name, annotation_attr in AnnotationType.types.items():
                if hasattr(method, annotation_attr):
                    annotationMetadata.add_method_annotation(method, annotation_name, getattr(method, annotation_attr))

        return annotationMetadata
