

class AdviceTarget:
    def __init__(self, advice_method, target_bean, target_methods):
        # 切入逻辑
        self.advice_method = advice_method
        # 目标bean
        self.target_bean = target_bean
        # 目标bean上需要切入的方法
        self.target_methods = target_methods
