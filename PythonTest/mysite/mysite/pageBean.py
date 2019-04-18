
# 使用 pagebean 实现分页
class PageTest:
    _pageNo =0
    _pageSize = 0
    _totalPage = 0
    _totalCount = 0
    _startNum = 0
    def getPageNo(self):
        return self._pageNo
    def setPageNo(self,value):
        self._pageNo = value

    def getPageSize(self):
        return self._pageSize
    def setPageSize(self,value):
        self._pageSize = value

    def getTotalPage(self):
        return self._totalPage
    def setTotalPage(self,value):
        self._totalPage = value

    def getTotalCount(self):
        return self._totalCount
    def setTotalCount(self,value):
        self._totalCount = value

    def getStartNum(self):
        return self._startNum
    def setStartNum(self,value):
        self._startNum = value

    def __init__(self,pageNo,pageSize,totalCount):
        self._pageNo = pageNo
        self._pageSize = pageSize
        if (totalCount == 0):
            self._totalPage = 1
        else:
            # Python 取余 以及 三目运算符 与其他语言不一样
            self._totalPage = (totalCount//pageSize) if (totalCount%pageSize == 0) else (totalCount//pageSize + 1)
            # self._totalPage = 2
        self._totalCount = totalCount
        self._startNum = (pageNo - 1) * pageSize