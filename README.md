# pySimpleSpringFramework
模仿 java spring 实现的简易python版

一.  装饰器

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



二.  代码模块创建器

 http服务使用的是 fastapi

```python
import pySimpleSpringFramework.spring_core.util.codeGenerator.generator
if __name__ == '__main__':   			      pySimpleSpringFramework.spring_core.util.codeGenerator.generator.AppCodeGenerator.generate_app_and_rest_template()
```

指定以上代码后会创建3个文件:

```
1. applicationStarter.py
2. restService.py
3. start.py
```

自己修改好后，执行 start.py 启动程序