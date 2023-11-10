import abc


class PyDatabaseConnectivity(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def raw_query(self, sql):
        pass

    @abc.abstractmethod
    def raw_execute(self, *sqls):
        pass

    @abc.abstractmethod
    def raw_commit(self):
        pass

    @abc.abstractmethod
    def raw_rollback(self):
        pass

    @abc.abstractmethod
    def raw_close(self):
        pass
