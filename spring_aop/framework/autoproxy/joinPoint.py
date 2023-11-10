class JoinPoint:
    def __init__(self, target, method, *args, **kwargs):
        self.target = target
        self.method = method
        self.args = args
        self.kwargs = kwargs


class ProceedJoinPoint:
    def __init__(self, join_point):
        self.join_point = join_point
        self.next_proceed_join_point = None

    def set_next_proceed_join_point(self, proceed_join_point):
        self.next_proceed_join_point = proceed_join_point

    def get_args(self):
        return self.join_point.args, self.join_point.kwargs

    def proceed(self):
        return self.join_point.method(*self.join_point.args, **self.join_point.kwargs)
