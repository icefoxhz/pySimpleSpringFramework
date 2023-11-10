pySimpleSpringFramework

模仿 java spring 实现的简易python版

# 一.  装饰器

使用装饰器可以像java中使用注解一样

```python
1. ComponentScan 
	类装饰器，添加要扫描的模块，支持多个
    
    @ComponentScan("../../test_modules1", "../../test_modules2")
    class ServiceApplication(ApplicationStarter):
        pass
    
2. ConfigDirectories
	类装饰器，添加要扫描的配置文件目录
    
    @ConfigDirectories("../../config")
    class ServiceApplication(ApplicationStarter):
        pass

3. Component
	类装饰器，标记为组件，从而可以被扫描到。默认为单例
    
    @Component
    class A:
        pass
    
4. Order
	类/方法 装饰器, 排序（从小到大）
    @Component
    @Order(1)
    class A:
        pass
    
5. Autowired
	方法 装饰器, 注入 bean，方法名必须以 set 或 _set 开头. 例子如下: 
    
    @Component
    class A:
        pass
    
    @Component
    class B:
        @Autowired
        def set_params(self, a):
            self.a = a
    
6. Value
	方法 装饰器, 注入配置文件信息。 
    
    @Component
    class A:
   		@Value({"spring.profiles.include": "v1"})
        def __init__(self):
            self.v1 = None
    
    spring.profiles.include为配置文件的 key, v1 是自己定义的变量， 把对应的值赋值给 self.v1
    
7. Scope
	类 装饰器, SCOPE("singleton") / SCOPE("prototype") ， singleton为单例， prototype为原型
    
    @Component
    @Scope("prototype")
    class A:
        pass

8. Aspect
	类 装饰器, 标记为AOP类
    
    @Component
    @Aspect
    class AspectTest1:
        pass
    
9. Pointcut
	方法 装饰器, 定义切入点. 例子如下:
        
    @Pointcut({"execution": ["A.f1", "B.f2"]})
    def aspectPointcut1(self):
        pass
    
   	@Pointcut({"execution": ["*.*"]})
    def aspectPointcut2(self):
        pass
    
10. Before
	方法 装饰器
    
	@Before(["aspectPointcut1"])
    def aspectBefore1(self, joinPoint):
        print(">>>>>>>>> aspectBefore1 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)
        
11. After
	方法 装饰器
    
	@After(["aspectPointcut1", "aspectPointcut4"])
    def aspectAfter1(self, joinPoint):
        print(">>>>>>>>> aspectAfter1 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)
        
12. AfterReturning
	方法 装饰器
    
    def aspectAfterReturning2(self, joinPoint, return_object):
        print(">>>>>>>>> aspectAfterReturning2 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
        joinPoint.kwargs,
        return_object)

13. AfterReturning
	方法 装饰器
    
    def aspectAfterReturning3(self, joinPoint, return_object):
        return_object.return_value = return_object.return_value + 10
        print(">>>>>>>>> aspectAfterReturning3 = > ", joinPoint.target, joinPoint.method, joinPoint.args, 
        joinPoint.kwargs, 
        return_object)        

14. Round
	方法 装饰器, 这个比较特殊，不自动调用原方法，需要自己调用
    
    @Around(["aspectPointcut1"])
    def aspectAround2(self, proceed_join_point):
        print(">>>>>>>>>  around before aspectAround2", proceed_join_point)
        result = proceed_join_point.proceed()
        # print("执行程序，返回结果: ", result)
        print(">>>>>>>>>  around after aspectAround2", proceed_join_point)
        return result

15. Ds
	类/方法 装饰器,切换数据源。 类上加的话，所有方法都会切换到指定数据源，方法上的优先级最高
    
    @Component
    @Ds("ds1")
    class A:
        @Ds("ds2")
        def insert_user():
            pass
    
    
16. Select、Insert、update、Delete
	方法 装饰器
   
	@Component
    class Mapping:
        @Select("select * from user")
        def get_users(self):
            pass

        @Insert("insert into user values('#{username}', '#{password}')")
        def insert_user1(self, username, password):
            pass

        @Update("update user set password='#{password}' where username='#{username}'")
        def insert_user2(self, username, password):
            pass

        @Delete("delete from user")
        def delete_users(self):
            pass
    
17. Transactional
	类/方法 装饰器. 
    @Transactional(Propagation.REQUIRED) :  如果当前没有事物就创建一个事务，如果已有就使用当前事务
    @Transactional(Propagation.REQUIRES_NEW): 启用一个新事物执行
    
    @Component
	@Transactional()  # 默认为 Propagation.REQUIRED
    class DsTest:
        @Transactional(Propagation.REQUIRES)
        def insert_user1(self, username, password):
            self._mapping.insert_user(username, password)
    	
        @Transactional(Propagation.REQUIRES_NEW)
        def insert_user2(self, username, password):
            self._mapping.insert_user(username, password)

18. Sync
	方法 装饰器. 启用异步任务。 调用的时候和普通方法一样调用，框架会自动使用多线程执行
    
    @Component
    class A:
        @Sync
        def task1():
            return "ok"
       	
        @Sync
        def task2():
            pass
    
    
```

# 二.  配置文件

配置文件使用 yaml 和 properties ，和java 一样。

目录结构如下 :

```
config
   application.properties
   application-dev.properties
   application-dev.yaml
   application-prod.properties
   application-prod.yaml
```



application.properties

```
# 指定使用哪个配置
spring.profiles.include=dev
```



application-dev.yaml  

数据库配置和线程池配置如下: 

```yaml
datasource:
  debug_sql: true
  sources:
    # 数据源1
    source1:
      url: mysql+pymysql://127.0.0.1:3306/hz_test
      username: root
      password: 112233QQwwee
  #    connect_args: {"options": "-c search_path=public"}
      # 如果不设置就全部使用默认值
      pool:
        #    -pool_size=5, 连接数大小，默认为 5，正式环境该数值太小，需根据实际情况调大
        size: 20
        #    -pool_recycle, 默认为 600, 推荐设置为 7200, 即如果 connection 空闲了 7200 秒，自动重新获取，以防止 connection 被 db server 关闭。
        recycle: 600
        #    -max_overflow=10, 超出 pool_size 后可允许的最大连接数，默认为 10, 这 10 个连接在使用过后，不放在 pool 中，而是被真正关闭的。
        max_overflow: 1000
        #    -pool_timeout=30, 获取连接的超时阈值，默认为 30 秒
        timeout: 10
    # 数据源2
    source2:
      url: mysql+pymysql://127.0.0.1:3306/test
      username: root
      password: 112233QQwwee
      pool:
        size: 20
        recycle: 600
        max_overflow: 1000
        timeout: 10


# 不设置默认为当前机器的cpu数量
task:
  execution:
    pool:
      max_size: 20      # 设置线程池的最大线程数


```

# 三.  代码模块创建器

```python
from pySimpleSpringFramework.spring_core.util.codeGenerator.generator import AppCodeGenerator

if __name__ == '__main__':
    AppCodeGenerator.generate_app_and_rest_template()
    # 如果不需要 http服务，使用 AppCodeGenerator.generate_app_template

```



指定以上代码后会创建3个文件:

1. applicationStarter.py  类似java springboot的 SpringApplication

```python
import os
import sys

from pySimpleSpringFramework.spring_core.applicationStarter import ApplicationStarter
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import ComponentScan, ConfigDirectories


# 把父目录放入path， 父目录就是包。 这个需要自己调整
root_model_path = os.path.dirname(os.path.dirname(os.getcwd()))
print("root_model_path=", root_model_path)
sys.path.append(root_model_path)


# 基于 root_model_path 的相对的位置， 因为 root_model_path 就是包
@ComponentScan("../../pySimpleSpringFramework/spring_test/test_modules")
# 这里修改成自己的配置文件位置（相对当前这个启动文件的位置）
@ConfigDirectories("../../config")
class ServiceApplication(ApplicationStarter):
    def __init__(self):
        super().__init__()
        self.__application_context = None
    
    @property
    def application_context(self):
        return self.__application_context

    def main(self, application_context):
        self.__application_context = application_context
        
        # 这里执行自己的启动逻辑
        # ...


serviceApplication = ServiceApplication()

if __name__ == '__main__':
    serviceApplication.run(True)

        
```



2. restService.py  

   使用 fastapi 作为http服务组件。你也可以用自己喜欢的

```python

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# 在这里导入自己的serviceApplication实例
from pySimpleSpringFramework.spring_test.applicationStarter import serviceApplication

rest_app = FastAPI()


@rest_app.get("/get_test/id={opId}")
async def get_template(opId: int):
    print("opId = ", opId)
    # 这里是获取bean的例子
    # myBean = serviceApplication.application_context.get_bean("myBean")
    return "ok"


class TodoItem(BaseModel):
    title: str
    description: str


@rest_app.post("/post_test", response_model=TodoItem)
async def post_template(todo: TodoItem):
    # 这里是获取bean的例子
    dsTest = serviceApplication.application_context.get_bean("dsTest")
    try:
        dsTest.delete_users()
    except:
        pass

    print("insert_user: ", dsTest.insert_user('ww', '112345'))
    print(dsTest.get_users())
    return todo


def start_rest_service(port):
    # 启动rest服务
    uvicorn.run(rest_app, host="0.0.0.0", port=port, reload=False)

            
```



3. start.py

```python
# 在这里导入自己的serviceApplication 和 start_rest_service
from pySimpleSpringFramework.spring_test.applicationStarter import serviceApplication
from pySimpleSpringFramework.spring_test.restService import start_rest_service


if __name__ == '__main__':
    # 启动app
    serviceApplication.run(True)

    # 启动rest服务
    start_rest_service(8000)

```

根据自己实际情况修改好后，执行 start.py 启动程序

