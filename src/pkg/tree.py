# 节点树
import typing as t

from .node import Node, Data
from .notebook import Notebooks
from .client import Client, IDocs


class Tree(object):
    """
    节点树
    """
    @classmethod
    def fromDict(cls, d: t.Dict[str, t.Any]) -> 'Tree':
        """ 从字典创建节点 """
        return cls(
            root=Node.fromDict(d['root']),
            client=Client.fromDict(d['client']),
            notebooks=Notebooks.fromList(d['notebooks'])
        )

    def __init__(
        self,
        root: Node = Node(),
        client: Client = Client(),
        notebooks: Notebooks = Notebooks(),
    ):
        self._root: Node = root  # 根节点
        self._client = client  # 思源服务客户端
        self._notebooks = notebooks  # 笔记本列表
        self._map: t.Dict[str, Node] = dict()  # 节点 ID -> node 映射

    def __dict__(self) -> t.Dict[str, t.Any]:
        return {
            'root': self._root.__dict__(),
            'client': self._client.__dict__(),
            'notebooks': self._notebooks.__dict__(),
        }

    def __repr__(self) -> str:
        return self._root.__repr__(0)

    def id2node(self, id: str) -> t.Optional[Node]:
        return self._map.get(id)

    def buildTree(self, *ids: t.List[str]) -> None:
        """ 构造树 """
        self.buildDocTree(*ids)
        self.buildBlockTree(*ids)

    def buildDocTree(self, *ids: t.List[str]) -> None:
        """ 构造文档树 """
        for node_id in ids:
            if self._notebooks.isNotebookID(id=node_id):
                self._buildDocTreeFromNotebookID(box=node_id)
            else:
                self._buildDocTreeFromDocID(root_id=node_id)

    def buildBlockTree(self, *ids: t.List[str]) -> None:
        """ 构造块树 """
        for node_id in ids:
            if self._notebooks.isNotebookID(id=node_id):
                self._buildBlockTreeFromNotebookID(box=node_id)
            else:
                self._buildBlockTreeFromDocID(root_id=node_id)

    def _parseDocPath(
        self,
        notebook: Node,
        path: str,
        hpath: str,
    ) -> t.Tuple[t.List[str], t.List[str], int]:
        """ 解析路径 """
        paths = f"{notebook.id}{path[:-3]}".split('/')  # ID 路径列表
        hpaths = f"{notebook.data.content}{hpath}".split('/')  # 标题路径列表
        depth: int = min(len(paths), len(hpaths))  # 文档深度(包含笔记本级别)

        return (
            paths,
            hpaths,
            depth,
        )

    def _addNotebookNode(
        self,
        id: str,
        name: str,
    ) -> Node:
        """ 插入一个笔记本节点 """
        node_notebook = self.id2node(id)
        if node_notebook is not None:
            return node_notebook
        else:
            node_notebook = Node(
                id=id,
                data=Data(
                    content=name,
                ),
            )
            self._root.addChild(node_notebook)
            self._map[node_notebook.id] = node_notebook

            return node_notebook

    def _addNode(
        self,
        node_parent: Node,
        id: str,
        data: Data,
    ) -> Node:
        """ 插入一个节点 """
        node = self.id2node(id)
        if node is not None:
            return node
        else:
            node = Node(
                id=id,
                data=data,
            )
            node_parent.addChild(node)
            self._map[node.id] = node

            return node

    def _buildSubTreeFromDocList(
        self,
        node_default: Node,
        node_notebook: Node,
        docs: IDocs,
    ) -> None:
        """ 从文档列表构建下级文档树 """

        node_parent = node_default
        for doc in docs:
            # 解析文档路径
            paths, _, depth = self._parseDocPath(node_notebook, doc['path'], doc['hpath'])
            if depth >= 2:
                # 按需更新上级节点
                parent_id = paths[-2]
                if node_parent.id != parent_id:
                    node_parent = self.id2node(parent_id)

                if node_parent is not None:
                    # 插入节点
                    self._addNode(
                        node_parent=node_parent,
                        id=doc['id'],
                        data=Data.fromQueryResult(doc),
                    )
                else:
                    node_parent = node_default

    def _buildDocTreeFromNotebookID(self, box: str) -> None:
        """ 从笔记本构建文档树 """

        # 将笔记本插入树
        node_notebook = self._addNotebookNode(id=box, name=self._notebooks.id2name(box))

        # 使用 SQL 查询该笔记本的子文档
        docs: IDocs = self._client.queryDocsFromBox(box)

        # 通过查询结果构造文档树
        self._buildSubTreeFromDocList(
            node_default=node_notebook,
            node_notebook=node_notebook,
            docs=docs,
        )

    def _buildDocTreeFromDocID(self, root_id: str) -> None:
        """ 从文档构建文档树 """
        # 查询文档信息
        result: IDocs = self._client.queryDocFromDocID(root_id)
        if len(result) > 0:
            doc = result[0]
            # 获得笔记本节点
            node_notebook = self._addNotebookNode(id=doc['box'], name=self._notebooks.id2name(doc['box']))

            # 获得文档路径
            paths, _, depth = self._parseDocPath(node_notebook, doc['path'], doc['hpath'])

            # 构建该文档的上级节点
            node_parent = node_notebook
            for i in range(1, depth - 2):
                response = self._client.queryDocFromDocID(paths[i])
                if len(response.body) > 0:
                    parent_doc = response.body[0]
                    node = self._addNode(
                        node_parent=node_parent,
                        id=parent_doc['id'],
                        data=Data.fromQueryResult(parent_doc),
                    )
                    node_parent = node
                else:
                    break
            node_parent = self._addNode(
                node_parent=node_parent,
                id=doc['id'],
                data=Data.fromQueryResult(doc),
            )

            # 构建该文档的下级节点
            # 使用 SQL 查询该文档的子文档
            docs: IDocs = self._client.querySubdocsFromDocID(doc['id'])

            # 通过查询结果构造文档树
            self._buildSubTreeFromDocList(
                node_default=node_parent,
                node_notebook=node_notebook,
                docs=docs,
            )
