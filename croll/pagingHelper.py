class pagingHelper:
    "paging helper class"

    def getTotalPageList(self, total_cnt, rowsPerPage):
        if ((total_cnt % rowsPerPage) == 0):
            self.total_pages = int(total_cnt / rowsPerPage);

        else:
            self.total_pages = int((total_cnt / rowsPerPage)) + 1;

        self.totalPageList = []
        # self.total_pages=0 #삽입
        for j in range(self.total_pages):
            self.totalPageList.append(j + 1)

        return self.totalPageList

    def __init__(self):
        self.total_pages = 0
        self.totalPageList = 0