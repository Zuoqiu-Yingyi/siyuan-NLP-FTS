# -*- coding: utf-8 -*-
# 定义节点
import json
import typing as t


class Data(object):
    """
    节点数据
    """

    @classmethod
    def fromDict(cls, data: t.Dict[str, t.Union[str, t.Set[str]]]) -> 'Data':
        """ 从字典创建节点 """
        return cls(
            content=data['content'],
            name=data['name'],
            memo=data['memo'],
            alias=set(data['alias']),
            keys=set(data['keys']),
            keys_with_inherit=set(data['keys_with_inherit']),
        )

    @ classmethod
    def fromQueryResult(cls, result: t.Dict[str, t.Union[str, int]]) -> 'Data':
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
        keys_with_inherit: t.Optional[t.Set[str]] = None,  # 块关键词集合（包含继承）
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
        self._keys_with_inherit = keys_with_inherit if keys_with_inherit else set()

    def __dict__(self) -> dict:
        return {
            'content': self.content,
            'name': self.name,
            'memo': self.memo,
            'alias': list(self.alias),
            'keys': list(self.keys),
            'keys_with_inherit': list(self.keys_with_inherit),
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

    @ property
    def keys_with_inherit(self) -> t.Set[str]:
        return self._keys_with_inherit

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

    def inheritKeys(self, parent: 'Data') -> None:
        """ 继承关键词 """
        self._keys_with_inherit.clear()
        self._keys_with_inherit.update(self._keys)
        self._keys_with_inherit.update(parent.keys_with_inherit)


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
        self.data = data if data else Data()

        for child in self._children:
            child.setParent(self, False)

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

    def __str__(self, indent: int = 2) -> str:
        return json.dumps(self.__dict__(), ensure_ascii=False, indent=indent)

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

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

    @ property
    def isLeaf(self) -> bool:
        return len(self._children) == 0

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
        self._parent_id = parent.id
        if parent is not None:
            self._parent_id = parent.id
            if cascade:
                parent.addChild(child=self, cascade=False)
        return self
