
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from pySimpleSpringFramework.spring_test.applicationStarter import serviceApplication

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

            