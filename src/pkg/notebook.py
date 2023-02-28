# 笔记本
import typing as t


class Notebook(object):
    """
    笔记本
    """

    @classmethod
    def fromDict(cls, d: dict) -> 'Notebook':
        return cls(
            id=d['id'],
            icon=d['icon'],
            name=d['name'],
            sort=d['sort'],
            closed=d['closed'],
        )

    def __init__(
        self,
        id: str,
        icon: str,
        name: str,
        sort: int,
        closed: bool,
    ):
        self.id = id  # 笔记本 ID
        self.icon = icon  # 笔记本图标
        self.name = name  # 笔记本名称
        self.sort = sort  # 笔记本排序
        self.closed = closed  # 笔记本是否关闭

    def __dict__(self) -> dict:
        return {
            'id': self.id,
            'icon': self.icon,
            'name': self.name,
            'sort': self.sort,
            'closed': self.closed,
        }


class Notebooks(object):
    """
    笔记本列表
    """

    def __init__(self, notebooks: t.List[Notebook] = []):
        notebooks.sort(key=lambda n: n.sort)
        self.notebooks = notebooks
        self._map = {n.id: n for n in notebooks}

    def id2name(self, id: str) -> str:
        notebook = self._map.get(id)
        return notebook.name if notebook else ''
    
    def isNotebookID(self, id: str) -> bool:
        if id in self._map:
            return False if self._map[id].closed else True
        else:
            return False
