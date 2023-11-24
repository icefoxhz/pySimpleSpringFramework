import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from pySimpleSpringFramework.spring_test.applicationEntrypoint import serviceApplication

app = FastAPI()


@app.get("/myId={test_id}")
async def getTest(test_id: int):
    print("test_id = ", test_id)
    dsTest = serviceApplication.application_context.get_bean("dsTest")
    print(dsTest)

    return "ok => id =" + str(test_id)


# 创建一个Pydantic模型来表示待办事项
class TodoItem(BaseModel):
    title: str
    description: str


@app.post("/todos", response_model=TodoItem)
async def postTest(todo: TodoItem):
    print(todo)
    dsTest = serviceApplication.application_context.get_bean("dsTest")
    try:
        dsTest.delete_users()
    except:
        pass

    print("insert_user: ", dsTest.insert_user('ww', '112345'))
    print(dsTest.get_users())

    return todo


if __name__ == '__main__':
    serviceApplication.run(True)

    # 启动Sanic应用
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
