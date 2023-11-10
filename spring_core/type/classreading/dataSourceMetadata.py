from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Pointcut
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName
from pySimpleSpringFramework.spring_core.type.classreading.annotationMetadata import AnnotationMetadata
from pySimpleSpringFramework.spring_orm.dsAopTemplate import DataSourceAopTemplate


class DataSourceMetadata:
    def __init__(self, cls):
        self.cls = cls
        self._metadata = None

    def set_metadata(self, ds_metadata):
        self._metadata = ds_metadata

    @property
    def ds_metadata(self):
        return self._metadata

    @staticmethod
    def introspect(annotation_metadata: AnnotationMetadata):
        data_source_metadata = None

        metadata_map = {}
        metadata_ds = annotation_metadata.get_methods(AnnotationName.DS)
        if len(metadata_ds) > 0:
            metadata_map[AnnotationName.DS] = metadata_ds

        metadata_select = annotation_metadata.get_methods(AnnotationName.SELECT)
        if len(metadata_select) > 0:
            metadata_map[AnnotationName.SELECT] = metadata_select

        metadata_transactional = annotation_metadata.get_methods(AnnotationName.TRANSACTIONAL)
        if len(metadata_transactional) > 0:
            metadata_map[AnnotationName.TRANSACTIONAL] = metadata_transactional

        metadata_execute = annotation_metadata.get_methods(AnnotationName.EXECUTE)
        if len(metadata_execute) > 0:
            metadata_map[AnnotationName.EXECUTE] = metadata_execute

        if len(metadata_map) > 0:
            cls = annotation_metadata.cls
            data_source_metadata = DataSourceMetadata(cls)
            data_source_metadata.set_metadata(metadata_map)

        return data_source_metadata
