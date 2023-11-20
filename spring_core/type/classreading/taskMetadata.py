from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName
from pySimpleSpringFramework.spring_core.type.classreading.annotationMetadata import AnnotationMetadata


class TaskMetadata:
    def __init__(self, cls):
        self.cls = cls
        self._metadata = {}

    def set_metadata(self, annotationName, metadata):
        self._metadata[annotationName] = metadata

    @property
    def task_metadata(self):
        return self._metadata

    @staticmethod
    def introspect(annotation_metadata: AnnotationMetadata):
        task_metadata = None

        metadata_task = annotation_metadata.get_methods(AnnotationName.SYNC)
        if len(metadata_task) > 0:
            if task_metadata is None:
                task_metadata = TaskMetadata(annotation_metadata.cls)
            task_metadata.set_metadata(AnnotationName.SYNC, metadata_task)

        metadata_task = annotation_metadata.get_methods(AnnotationName.NEW_THREAD_POOL)
        if len(metadata_task) > 0:
            if task_metadata is None:
                task_metadata = TaskMetadata(annotation_metadata.cls)
            task_metadata.set_metadata(AnnotationName.NEW_THREAD_POOL, metadata_task)

        return task_metadata
