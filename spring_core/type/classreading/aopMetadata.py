import sys

from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName, AnnotationType
from pySimpleSpringFramework.spring_core.util.commonUtils import get_bean_name_by_class_name


class AopMetadata:
    __SPLIT_SYMBOL = "."

    def __init__(self, cls):
        self.cls = cls
        self.__order_attr = AnnotationType.get_annotation_attr(AnnotationName.ORDER)
        """
        {
            "aspectPointcut1": {"execution": ["*.my_print", "LoginService.login", "*.*"]},
            ...
        }
        """
        self._pointcuts = {}

        """
        {
            "aspectPointcut1": {"*": ["*"], "LoginService": ["login"]},
            ...
        }
        
        """
        self._pointcuts_parsed = {}

        """
        {
            AnnotationName.BEFORE : {
                                        method1: ["aspectPointcut1", "aspectPointcut3"],
                                        method2: ["aspectPointcut2"],
                                        ...
                                    },
            AnnotationName.AFTER: {
                                    ...
                                   }
            ...
        }
        """
        self._advices = {}
        self._candidate_bean_names = []

    @property
    def pointcuts(self) -> dict:
        return self._pointcuts

    @property
    def pointcuts_parsed(self) -> dict:
        return self._pointcuts_parsed

    @property
    def advices(self) -> dict:
        return self._advices

    @property
    def candidate_bean_names(self) -> list:
        return self._candidate_bean_names

    def add_pointcuts(self, methods):
        for method, value in methods.items():
            method_name = method.__name__
            self._pointcuts[method_name] = value

    def parse_pointcuts(self):
        result = {}
        for pointcut_name, pointcut_execution in self._pointcuts.items():
            d = {}
            execution_list = pointcut_execution.get("execution", [])
            for execution in execution_list:
                ls = execution.split(self.__SPLIT_SYMBOL)
                if len(ls) != 2:
                    raise Exception("execution表达式不合法! 示例: *.*")

                class_name = ls[0]
                method_name = ls[1]

                # 获取要aop的类
                self._candidate_bean_names.append(get_bean_name_by_class_name(class_name))

                if class_name not in d:
                    d[class_name] = [method_name]
                    continue

                method_name_list = d.get(class_name)
                method_name_list.append(method_name)

                # 如果 method_name_list 中有一个是 * , 那其他就没有意义了，保留 *即可
                if "*" in method_name_list:
                    method_name_list = ["*"]

                d[class_name] = method_name_list

            result[pointcut_name] = d

        self._candidate_bean_names = list(set(self._candidate_bean_names))
        self._pointcuts_parsed = result

    def add_advices(self, annotation_name_advice, methods):
        advices = self._advices.get(annotation_name_advice, {})
        advices.update(methods)
        self._advices[annotation_name_advice] = advices

    def __order_advice_methods_func(self, item) -> int:
        method = item[0]
        return sys.maxsize if not hasattr(method, self.__order_attr) else getattr(method, self.__order_attr)

    def order_advices_methods(self):
        for advice_pos, advice_meta in self._advices.items():
            self._advices[advice_pos] = {k: v for k, v in
                                         sorted(advice_meta.items(), key=self.__order_advice_methods_func)}

    @staticmethod
    def introspect(annotation_metadata):
        aopMetadata = AopMetadata(annotation_metadata.cls)

        is_aspect = annotation_metadata.get_class_annotation(AnnotationName.ASPECT)
        if not is_aspect:
            return

        methods = annotation_metadata.get_methods(AnnotationName.POINTCUT)
        aopMetadata.add_pointcuts(methods)

        annotation_name_advices = [AnnotationName.BEFORE,
                                   AnnotationName.AFTER,
                                   AnnotationName.AFTER_RETURNING,
                                   AnnotationName.AFTER_THROWING,
                                   AnnotationName.ROUND]
        for annotation_name_advice in annotation_name_advices:
            methods = annotation_metadata.get_methods(annotation_name_advice)
            aopMetadata.add_advices(annotation_name_advice, methods)

        # 排序
        aopMetadata.order_advices_methods()

        # 解析出要的格式
        aopMetadata.parse_pointcuts()

        return aopMetadata
