# from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
# from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired
# from pySimpleSpringFramework.spring_core.type.annotationType import Propagation
# from pySimpleSpringFramework.spring_orm.annoation.dataSourceAnnotation import Transactional, DS
# from pySimpleSpringFramework.spring_test.test_modules.m1.ds_test.mapping import Mapping
#
#
# @Component
# # @Transactional(Propagation.REQUIRED)
# class DsTest:
#
#     def __init__(self):
#         self._dsTest = None
#         self._mapping = None
#
#     @Autowired
#     def set_params(self, mapping, dsTest):
#         self._mapping = mapping
#         self._dsTest = dsTest
#
#     def get_users(self):
#         return self._mapping.get_users()
#
#     @DS("source1")
#     @Transactional(Propagation.REQUIRED)
#     def insert_user1(self, username, password):
#         self._mapping.insert_user1(username, password)
#         # pass
#
#     @Transactional(Propagation.REQUIRES_NEW)
#     def insert_user2(self, username, password):
#         self._mapping.insert_user2(username, password)
#         # pass
#
#     @Transactional(Propagation.REQUIRED)
#     def insert_user(self):
#         self._dsTest.insert_user1('zs', '123123')
#         self._dsTest.insert_user2('ls', '3333')
