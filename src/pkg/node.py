# 定义节点
import typing as t


class Data(object):
    """
    节点数据
    """

    def __init__(
        self,
        content: str = "",
        name: str = "",
        memo: str = "",
        alias: t.Set[str] = {},
        keys: t.Set[str] = {},
    ):
        self._content = content  # 块内容
        self._name = name  # 块命名
        self._memo = memo  # 块备注
        self._alias = alias  # 块别名集合
        self._keys = keys  # 块关键词集合

    def __dict__(self) -> dict:
        return {
            'content': self._content,
            'name': self._name,
            'memo': self._memo,
            'alias': list(self._alias),
            'keys': list(self._keys),
        }

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, content: str) -> None:
        self._content = content

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def alias(self) -> t.Set[str]:
        return self._alias

    @alias.setter
    def alias(self, alias: str) -> None:
        self._alias.clear()
        self._alias.add(a.replace('\n', ',') for a in alias.replace('\\,', '\n').split(','))

    @property
    def memo(self) -> str:
        return self._memo

    @memo.setter
    def memo(self, memo: str) -> None:
        self._memo = memo

    @property
    def keys(self) -> t.Set[str]:
        return self._keys

    def analize(self) -> None:
        """ 提取关键词 """
        pass


class Node(object):
    """
    树节点
    """

    @classmethod
    def fromDict(cls, d: dict) -> 'Node':
        """ 从字典创建节点 """
        data = d['data']
        children = d['children']

        return cls(
            id=d['id'],
            parent_id=d['parent_id'],
            children=[cls.fromDict(child) for child in children],
            children_id=set(d['children_id']),
            data=Data(
                content=data['content'],
                name=data['name'],
                memo=data['memo'],
                alias=set(data['alias']),
                keys=set(data['keys']),
            ),
        )

    def __init__(
        self,
        id: str,  # 节点 id
        parent: t.Optional['Node'] = None,  # 上级节点
        parent_id: t.Optional[str] = None,  # 上级节点 id
        children: t.Set['Node'] = [],  # 下级节点
        children_id: t.Set[str] = [],  # 下级节点 id
        data: Data = None,  # 节点数据
    ):
        self._id = id
        self._parent = parent
        self._parent_id = parent_id
        self._children = children
        self._children_id = children_id
        self.data = data

    def __dict__(self) -> dict:
        return {
            'id': self._id,
            'parent_id': self._parent_id,
            'children': [n.__dict__() for n in self._children],
            'children_id': list(self._children_id),
            'data': self.data.__dict__(),
        }

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        return self._parent

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def children(self):
        return self._children

    @property
    def children_id(self):
        return self._children_id

    def addChild(self, node: 'Node'):
        """ 添加下级节点 """
        self._children.append(node)
        self._children_id.append(node.id)

    def setParent(self, parent: t.Optional['Node'] = None):
        self._parent = parent
        self._parent_id = parent.id
