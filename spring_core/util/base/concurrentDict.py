import threading


class ConcurrentDict:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def __reduce__(self):
        # 在序列化过程中排除线程锁
        return self.__class__, ()

    @property
    def size(self):
        # GIL 下 dict 的 len 原子，无需锁
        return len(self._data)

    def add(self, k, v):
        with self._lock:
            self._data[k] = v

    def get(self, k):
        # GIL 下 dict.get 原子，读不加锁（避免热路径每次取 bean 都拿锁）
        return self._data.get(k, None)

    def remove(self, k):
        with self._lock:
            if k in self._data:
                del self._data[k]

    def keys(self):
        return list(self._data.keys())

    def contains_key(self, k):
        return k in self._data

    def values(self):
        return list(self._data.values())

    def update(self, other_dict: dict):
        with self._lock:
            self._data.update(other_dict)
            
    def __getitem__(self, K):
        return self._data[K]

    def __setitem__(self, K, V):
        with self._lock:
            self._data[K] = V

    def items(self):
        return list(self._data.items())

    def __iter__(self):
        with self._lock:
            return iter(self._data)

    def clear(self):
        with self._lock:
            for v in self._data.values():
                del v
            self._data.clear()


if __name__ == '__main__':
    # 创建一个 ConcurrentDict 实例
    my_dict = ConcurrentDict()

    # 添加一些键值对
    my_dict.add("key1", "value1")
    my_dict.add("key2", "value2")
    my_dict.add("key3", "value3")

    # 添加一些键值对
    my_dict["1"] = "1"
    my_dict["2"] = "2"
    my_dict["3"] = "3"

    # 遍历字典
    for key, value in my_dict.items():
        print(f"Key: {key}, Value: {value}")
