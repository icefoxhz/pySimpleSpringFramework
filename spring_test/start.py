from pySimpleSpringFramework.spring_test.applicationStarter import serviceApplication
from pySimpleSpringFramework.spring_test.restService import start_rest_service

# 在这里导入自己的serviceApplication 和 start_rest_service

if __name__ == '__main__':
    # 启动app
    serviceApplication.run(True)

    # 启动rest服务
    start_rest_service(8000)
