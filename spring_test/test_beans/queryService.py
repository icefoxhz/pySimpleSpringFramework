from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotation.methodAnnotation import Autowired
from pySimpleSpringFramework.spring_orm.annoation.dataSourceAnnotation import Select, Transactional, DS
from pySimpleSpringFramework.spring_orm.databaseManager import DatabaseManager
from pySimpleSpringFramework.spring_test.test_beans.a import A


@Component
class QueryService:
    def __init__(self):
        self.a = A()
        self.b = None
        self.c = None
        self.databaseManager = None

    @Autowired
    def set_params(self, b, c, d):
        self.b = b
        self.c = c
        self.a.b = b
        self.a.d = d

    @Autowired
    def set_db_manager(self, databaseManager):
        self.databaseManager = databaseManager

    @DS("source1")
    @Transactional
    @Select("select * from user")
    def query_test(self):
        print("=======================  do QueryService's query_test =======================")
        df = self.databaseManager.query_to_df("select * from user")
        print(df)
        return df

    @Transactional
    def throw_test(self):
        print("thowing test")
        1 / 0
