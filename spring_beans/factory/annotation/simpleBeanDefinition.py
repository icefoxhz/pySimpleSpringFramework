from pySimpleSpringFramework.spring_core.type.classreading.annotationMetadata import AnnotationMetadata
from pySimpleSpringFramework.spring_core.type.classreading.aopMetadata import AopMetadata
from pySimpleSpringFramework.spring_core.type.classreading.beanMetadata import BeanMetadata
from pySimpleSpringFramework.spring_core.type.classreading.dataSourceMetadata import DataSourceMetadata
from pySimpleSpringFramework.spring_core.type.classreading.taskMetadata import TaskMetadata


class SimpleBeanDefinition:
    def __init__(self, cls):
        self.cls = cls
        self.name = cls.__name__
        self.model_path = None
        self._bean_metadata = None
        self._annotation_metadata = None
        self._aop_metadata = None

        self.__after_init()

    def __after_init(self):
        self._bean_metadata = BeanMetadata.introspect(self.cls)
        self._annotation_metadata = AnnotationMetadata.introspect(self._bean_metadata)
        self._aop_metadata = AopMetadata.introspect(self._annotation_metadata)
        self._ds_metadata = DataSourceMetadata.introspect(self._annotation_metadata)
        self._task_metadata = TaskMetadata.introspect(self._annotation_metadata)

    def get_annotation_metadata(self) -> AnnotationMetadata:
        return self._annotation_metadata

    def get_bean_metadata(self) -> BeanMetadata:
        return self._bean_metadata

    def get_aop_metadata(self) -> AopMetadata:
        return self._aop_metadata

    def get_ds_metadata(self) -> DataSourceMetadata:
        return self._ds_metadata

    def get_task_metadata(self) -> TaskMetadata:
        return self._task_metadata

    @staticmethod
    def generic_bean_definition(cls):
        return SimpleBeanDefinition(cls)
