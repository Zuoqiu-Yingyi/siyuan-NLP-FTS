# 定义节点
import typing as t


class Data(object):
    """
    节点数据
    """

    @classmethod
    def fromDict(cls, data: t.Dict[str, t.Union[str, t.Set[str]]]) -> 'Node':
        """ 从字典创建节点 """
        return cls(
            content=data['content'],
            name=data['name'],
            memo=data['memo'],
            alias=set(data['alias']),
            keys=set(data['keys']),
        )

    @ classmethod
    def fromQueryResult(cls, result: t.Dict[str, t.Union[str, int]]) -> 'Node':
        """ 从 SQL 查询结果创建节点 """
        return cls(
            content=result['content'],
            name=result['name'],
            memo=result['memo'],
            alias=result['alias'],
        )

    def __init__(
        self,
        content: str = "",  # 块内容
        name: str = "",  # 块命名
        memo: str = "",  # 块备注
        alias: t.Union[t.Set[str], str] = "",  # 块别名集合
        keys: t.Optional[t.Set[str]] = None,  # 块关键词集合
    ):
        self.content = content
        self.name = name
        self.memo = memo
        if isinstance(alias, set):
            self._alias = alias
        else:
            self._alias = set()
            self.alias = alias
        self._keys = keys if keys else set()

    def __dict__(self) -> dict:
        return {
            'content': self.content,
            'name': self.name,
            'memo': self.memo,
            'alias': list(self.alias),
            'keys': list(self.keys),
        }

    @ property
    def alias(self) -> t.Set[str]:
        return self._alias

    @ alias.setter
    def alias(self, alias: str) -> None:
        self._alias = set(filter(
            lambda s: not s.isspace() and len(s) > 0,  # 过滤空白字符
            [
                a.replace('\n', ',').strip()
                for a in alias.replace('\\,', '\n').split(',')
            ]
        ))

    @ property
    def memo(self) -> str:
        return self._memo

    @ memo.setter
    def memo(self, memo: str) -> None:
        self._memo = memo

    @ property
    def keys(self) -> t.Set[str]:
        return self._keys

    def extractKeys(self, extractor: t.Callable[[t.Set[str]], t.Set[str]]) -> None:
        """ 提取关键词 """
        sentences = set()
        if len(self.content) > 0 and not self.content.isspace():
            sentences.add(self.content)
        if len(self.name) > 0 and not self.content.isspace():
            sentences.add(self.name)
        if len(self.memo) > 0 and not self.content.isspace():
            sentences.update(set(self.memo.split('\n')))
        if len(self.alias) > 0:
            sentences.update(self.alias)

        self._keys.clear()
        if len(sentences) > 0:
            self._keys.update(extractor(sentences))


class Node(object):
    """
    树节点
    """

    @ classmethod
    def fromDict(cls, d: dict) -> 'Node':
        """ 从字典创建节点 """
        data = d.get('data')

        return cls(
            id=d.get('id'),
            parent_id=d.get('parent_id'),
            children=[cls.fromDict(child) for child in d.get('children', [])],
            children_id=set(d.get('children_id', [])),
            data=Data.fromDict(data) if data else None,
        )

    def __init__(
        self,
        id: str = 'root',  # 节点 id
        parent: t.Optional['Node'] = None,  # 上级节点
        parent_id: t.Optional[str] = None,  # 上级节点 id
        children: t.Optional[t.Set['Node']] = None,  # 下级节点
        children_id: t.Optional[t.Set[str]] = None,  # 下级节点 id
        data: t.Optional[Data] = None,  # 节点数据
    ):
        self._id = id
        self._parent = parent
        self._parent_id = parent_id
        self._children = children if children else set()
        self._children_id = children_id if children_id else set()
        self.data = data

    def __dict__(self) -> t.Dict[str, t.Any]:
        return {
            'id': self._id,
            'parent_id': self._parent_id,
            'children': list(map(lambda child: child.__dict__(), self._children)),
            'children_id': list(self._children_id),
            'data': self.data.__dict__() if self.data else None,
        }

    def __repr__(self, depth: int = 0) -> str:
        rows = []
        rows.append(f'{"| " * depth}- {self.data.content if self.data else self.id}')
        for child in self.children:
            rows.append(child.__repr__(depth + 1))
        return '\n'.join(rows)

    @ property
    def id(self):
        return self._id

    @ property
    def parent(self):
        return self._parent

    @ property
    def parent_id(self):
        return self._parent_id

    @ property
    def children(self):
        return self._children

    @ property
    def children_id(self):
        return self._children_id

    def addChild(
        self,
        child: 'Node',  # 下级节点
        cascade: bool = True,  # 是否级联绑定
    ) -> 'Node':
        """ 添加下级节点 """
        if child.id not in self._children_id:  # 避免重复添加
            self._children_id.add(child.id)
            self._children.add(child)
            if cascade:
                child.setParent(parent=self, cascade=False)
        return self

    def setParent(
        self,
        parent: t.Optional['Node'] = None,  # 上级节点
        cascade: bool = True,  # 是否级联绑定
    ) -> 'Node':
        """ 设置上级节点 """
        self._parent = parent
        if parent is not None:
            self._parent_id = parent.id
            if cascade:
                parent.addChild(child=self, cascade=False)
        return self
