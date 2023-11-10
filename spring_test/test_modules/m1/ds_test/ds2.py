from pySimpleSpringFramework.spring_core.task.annoation.taskAnnotation import Sync
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotationType import Propagation
from pySimpleSpringFramework.spring_orm.annoation.dataSourceAnnotation import Transactional, DS
from pySimpleSpringFramework.spring_test.test_modules.m1.ds_test.dsParent import DsParent


@Component
@Transactional()
@DS("source1")
class DsTest(DsParent):
    def get_users(self):
        return self._mapping.get_users()

    def insert_user1(self, username, password):
        return self._mapping.insert_user1(username, password)
        # pass

    # @DS("source2")
    @Transactional(Propagation.REQUIRES_NEW)
    def insert_user2(self, username, password):
        self._mapping.insert_user2(username, password)
        # pass

    @Sync
    def insert_user(self, username, password):
        return self._dsTest.insert_user1(username, password)
        # self._dsTest.insert_user2('ls', '3333')

    @Transactional(Propagation.REQUIRES_NEW)
    def delete_users(self):
        self._mapping.delete_users()
