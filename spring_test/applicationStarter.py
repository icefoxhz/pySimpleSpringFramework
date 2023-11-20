
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

        # applicationEnvironment = self.__application_context.get_bean("applicationEnvironment")
        # print(applicationEnvironment.get("MY_NAME"))

        import pickle
        serialized_data = pickle.dumps(application_context)
        print(serialized_data)
        deserialized_obj = pickle.loads(serialized_data)
        print(deserialized_obj)

        print("========= 完成 =========")


serviceApplication = ServiceApplication()

if __name__ == '__main__':
    serviceApplication.run(True)

        