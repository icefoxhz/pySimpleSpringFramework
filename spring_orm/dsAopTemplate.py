import inspect
import re
import threading

import numpy
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Before, AfterReturning, \
    AfterThrowing
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName, Propagation
from pySimpleSpringFramework.spring_core.util.commonUtils import get_init_propertiesEx
from pySimpleSpringFramework.spring_orm.databaseManager import DatabaseManager
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Order
from pySimpleSpringFramework.spring_orm.transferMeaningSymbol import transfer_meaning


class DataSourceAopTemplate:
    __local_obj = threading.local()

    def __init__(self):
        self._basic_types = (int, float, str)
        self._basic_string_types = ("numpy.int", "numpy.float", "numpy.str", "numpy.double", "numpy.long")
        self._exclude_types = (list, tuple)
        self._db_manager = None
        # self._debug_sql = False

    def set_db_manager(self, databaseManager: DatabaseManager):
        self._db_manager = databaseManager

    def set_environment(self, applicationEnvironment):
        app_environment = applicationEnvironment
        # self._debug_sql = app_environment.get("datasource.debug_sql", False)

    def _get_real_sqls(self, sql_list, cls_name, method, *args) -> list:
        """
        解析占位符，生成实际的sql
        :param sql_list:
        :param cls_name:
        :param method:
        :param args:
        :return:
        """
        field_to_value_dict = {}
        parameters = inspect.signature(method).parameters
        # 去掉参数中的 'self'
        parameter_names = [param for param in parameters if param != 'self']
        for i in range(len(parameter_names)):
            key = parameter_names[i]
            value = args[i]
            unknown_class = type(value)

            # 参数不支持
            if unknown_class in self._exclude_types:
                raise Exception("参数不支持类型：{}".format(self._exclude_types))

            # 字典类型处理
            if unknown_class == dict:
                if not key.endswith("_dict"):
                    log.warning(
                        "函数[ {}.{} ]中名为[ {} ]的参数是字典类型，建议的参数命名为 _dict 结尾".format(
                            cls_name,
                            method.__name__, key))
                field_to_value_dict.update(value)
                continue

            # 自定义类实例处理
            if unknown_class not in self._basic_types:
                is_find = False
                for string_type in self._basic_string_types:
                    if str(unknown_class).find(string_type) >= 0:
                        is_find = True
                        break

                if not is_find:
                    # 类名首字母小写的形式作为参数名
                    class_name = unknown_class.__name__
                    good_key = class_name[0].lower() + class_name[1:]
                    if key != good_key:
                        log.warning(
                            "函数[ {}.{} ]中名为[ {} ]的参数是类[ {} ]的实例，建议的参数命名为[ {} ]".format(
                                cls_name,
                                method.__name__,
                                key,
                                class_name,
                                good_key))
                    property_dict = get_init_propertiesEx(value)
                    field_to_value_dict.update(property_dict)
                    continue

            # 基本数据类型
            field_to_value_dict[key] = value

        sql_list_new = []
        for sql in sql_list:
            pattern = r"#{.*?}"
            matches = re.findall(pattern, sql)
            for match in matches:
                # 去掉可能的空格
                key = str(match).replace("#{", "").replace("}", "").strip()
                value = field_to_value_dict.get(key, None)
                if value is None:
                    raise Exception("{} 无法找到对应的值".format(match))
                sql = sql.replace(match, str(value))

            sql = transfer_meaning(sql)

            sql_list_new.append(sql)

        return sql_list_new

    # 待动态添加Pointcut表达式
    def aspectPointcutDs(self):
        pass

    # 待动态添加Pointcut表达式
    def aspectPointcutSelect(self):
        pass

    # 待动态添加Pointcut表达式
    def aspectPointcutExecute(self):
        pass

    # 待动态添加Pointcut表达式
    def aspectPointcutTransactional(self):
        pass

    @Order(1)
    @Before(["aspectPointcutDs"])
    def aspectDS(self, joinPoint):
        """
        实现 @DS 功能
        :param joinPoint:
        :return:
        """
        attr = AnnotationType.get_annotation_attr(AnnotationName.DS)
        if hasattr(joinPoint.method, attr):
            datasource_name = getattr(joinPoint.method, attr)
            self._db_manager.switch_datasource(datasource_name)

    @Order(2)
    @Before(["aspectPointcutTransactional"])
    def aspectStartTransaction(self, joinPoint):
        self._db_manager.set_autocommit(False)
        attr_trans = AnnotationType.get_annotation_attr(AnnotationName.TRANSACTIONAL)
        trans_type = getattr(joinPoint.method, attr_trans)
        if trans_type == Propagation.REQUIRED.value:
            is_create = self._db_manager.create_or_get_session()
            if is_create:
                self.__local_obj.trans_method = joinPoint.method

        if trans_type == Propagation.REQUIRES_NEW.value:
            self._db_manager.create_new_session()
            self.__local_obj.new_trans = True

    @Order(3)
    @AfterReturning(["aspectPointcutExecute"])
    def aspectExecute(self, joinPoint, return_object):
        attr_execute = AnnotationType.get_annotation_attr(AnnotationName.EXECUTE)
        if hasattr(joinPoint.method, attr_execute):
            sql = getattr(joinPoint.method, attr_execute)
            cls_name = joinPoint.target.__class__.__name__
            sql_list = self._get_real_sqls([sql], cls_name, joinPoint.method, *joinPoint.args)
            sql = sql_list[0]
            # if self._debug_sql:
            #     log.debug(sql)
            return_object.return_value = self._db_manager.raw_execute(sql)

    @Order(4)
    @AfterReturning(["aspectPointcutTransactional"])
    def aspectEndTransaction(self, joinPoint, return_object):
        if hasattr(self.__local_obj, "new_trans") and self.__local_obj.new_trans:
            self._db_manager.commit()
            self._db_manager.close()
            self._db_manager.recover_dstl()
            self.__local_obj.new_trans = False
            return

        if hasattr(self.__local_obj, "trans_method") and self.__local_obj.trans_method == joinPoint.method:
            self._db_manager.commit()
            self._db_manager.close()

    @Order(5)
    @AfterThrowing(["aspectPointcutTransactional"])
    def aspectAfterThrowing(self, joinPoint, ex):
        if hasattr(self.__local_obj, "trans_method") or hasattr(self.__local_obj, "new_trans"):
            self._db_manager.rollback()
            self._db_manager.close()
        if hasattr(self.__local_obj, "new_trans"):
            self._db_manager.recover_dstl()
        raise ex

    @Order(6)
    @AfterReturning(["aspectPointcutSelect"])
    def aspectSelect(self, joinPoint, return_object):
        """
        实现 @Select 功能
        :param joinPoint:
        :param return_object:
        :return:
        """
        attr = AnnotationType.get_annotation_attr(AnnotationName.SELECT)
        if hasattr(joinPoint.method, attr):
            sql = getattr(joinPoint.method, attr)
            cls_name = joinPoint.target.__class__.__name__
            sql_list = self._get_real_sqls([sql], cls_name, joinPoint.method, *joinPoint.args)
            sql = sql_list[0]
            # if self._debug_sql:
            #     log.debug(sql)
            return_object.return_value = self._db_manager.query_to_df(sql)
            self._db_manager.close()
