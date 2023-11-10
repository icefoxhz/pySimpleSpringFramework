from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_orm.annoation.dataSourceAnnotation import Select, Insert, Delete


@Component
class Mapping:
    @Select("select * from user")
    def get_users(self):
        pass

    @Insert("insert into user values('#{username}', '#{password}')")
    def insert_user1(self, username, password):
        pass

    @Insert("insert into user values('#{username}', '#{password}')")
    def insert_user2(self, username, password):
        pass

    @Delete("delete from user")
    def delete_users(self):
        pass
