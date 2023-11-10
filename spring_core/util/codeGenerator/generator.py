import os.path


class AppCodeGenerator:
    """
    创建入口文件
    """

    @staticmethod
    def generate_app_template(file_path, overwrite=False):
        # 如果文件存在就报错
        if os.path.exists(file_path) and not overwrite:
            raise Exception("{} 已经存在".format(file_path))

        code = """
import os
import sys

from pySimpleSpringFramework.spring_core.applicationStarter import ApplicationStarter
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import ComponentScan, ConfigDirectories


# 把父目录放入path， 父目录就是包。 这个需要自己调整
root_model_path = os.path.dirname(os.path.dirname(os.getcwd()))
print("root_model_path=", root_model_path)
sys.path.append(root_model_path)


# 基于 root_model_path 的相对的位置， 因为 root_model_path 就是包
@ComponentScan("../myProject/module1")
# 这里修改成自己的配置文件位置（相对当前这个启动文件的位置）
@ConfigDirectories("../config")
class ServiceApplication(ApplicationStarter):
    def __init__(self):
        super().__init__()
        self.__application_context = None
    
    @property
    def application_context(self):
        return self.__application_context

    def main(self, application_context):
        self.__application_context = application_context
    
        # 这里写自己的启动逻辑, 以下是一个示例
        # service = self.__application_context.get_bean("service")
        # service.run()


serviceApplication = ServiceApplication()

if __name__ == '__main__':
    serviceApplication.run(True)

        """

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

    @staticmethod
    def generate_rest_service_template(file_path, overwrite=False):
        # 如果文件存在就报错
        if os.path.exists(file_path) and not overwrite:
            raise Exception("{} 已经存在".format(file_path))

        code = """
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# 在这里导入自己的serviceApplication实例

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
    # myBean = serviceApplication.application_context.get_bean("myBean")
    return todo


def start_rest_service(port):
    # 启动rest服务
    uvicorn.run(rest_app, host="0.0.0.0", port=port, reload=False)

            """

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

    @staticmethod
    def __generate_start(file_path):
        code = """

# 在这里导入自己的serviceApplication 和 start_rest_service

if __name__ == '__main__':
    # 启动app
    serviceApplication.run(True)

    # 启动rest服务
    start_rest_service(8000)

            """

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

    @staticmethod
    def generate_app_and_rest_template():
        AppCodeGenerator.generate_app_template("applicationStarter.py", True)
        AppCodeGenerator.generate_rest_service_template("restService.py", True)
        AppCodeGenerator.__generate_start("start.py")


if __name__ == '__main__':
    AppCodeGenerator.generate_app_template("app.py", True)
    AppCodeGenerator.generate_rest_service_template("rest_service.py", True)


