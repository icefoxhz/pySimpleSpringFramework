核心库:
conda install pandas  -c conda-forge -y

conda install colorlog  -c conda-forge -y

pip install PyYAML -i  https://pypi.tuna.tsinghua.edu.cn/simple/

pip install sqlalchemy -i  https://pypi.tuna.tsinghua.edu.cn/simple/

pip install uvicorn -i  https://pypi.tuna.tsinghua.edu.cn/simple/

pip install fastapi -i  https://pypi.tuna.tsinghua.edu.cn/simple/

pip install tqdm -i  https://pypi.tuna.tsinghua.edu.cn/simple/

pip install requests -i  https://pypi.tuna.tsinghua.edu.cn/simple/


使用软链接，就不用每个虚拟环境都拷贝一次了，也方便维护
mklink /d "E:\windows_install\Miniconda3\envs\addressSearchpy311\Lib\site-packages\pySimpleSpringFramework" "D:\project\python\self\pySimpleSpringProject\2.0\pySimpleSpringFramework"