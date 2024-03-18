

class SingleIndexInfo():
    def __init__(self, index_ts_code):
        self.index_ts_code = index_ts_code
        self.index_name = None

        # TODO 或许看一下正规的django app里，如何定义数据模型，像springboot里类似DAO一样