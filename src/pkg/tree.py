# 节点树
import json
import typing as t

from .node import Node, Data
from .notebook import Notebooks
from .client import Client, IBlocks


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

        for node in self:
            self._map[node.id] = node

    def __dict__(self) -> t.Dict[str, t.Any]:
        return {
            'root': self._root.__dict__(),
            'client': self._client.__dict__(),
            'notebooks': self._notebooks.__dict__(),
        }

    def __repr__(self) -> str:
        """ 打印树结构 """
        return self._root.__repr__(0)

    def __str__(self, indent: int = 2) -> str:
        """ JSON 序列化结果 """
        return json.dumps(self.__dict__(), ensure_ascii=False, indent=indent)

    def __iter__(self):
        """ 深度优先遍历非根节点 """
        for child in self._root.children:
            yield from child

    def __len__(self) -> int:
        """ 非根节点数量 """
        return len(self._map)

    def id2node(self, node_id: str) -> t.Optional[Node]:
        return self._map.get(node_id)
    
    def getBreadcrumb(self, node_id: str) -> t.List[Node]:
        """ 获取节点的面包屑 """
        breadcrumb = []
        node = self.id2node(node_id)
        while node.parent:
            breadcrumb.append(node)
            node = node.parent
        return list(reversed(breadcrumb))

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
        docs: IBlocks,
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

        # 打印笔记本可读路径
        print(f"{box}: {node_notebook.data.content}")

        # 使用 SQL 查询该笔记本的子文档
        docs: IBlocks = self._client.queryDocsFromNotebookID(box)

        # 通过查询结果构造文档树
        self._buildSubTreeFromDocList(
            node_default=node_notebook,
            node_notebook=node_notebook,
            docs=docs,
        )

    def _buildDocTreeFromDocID(self, root_id: str) -> None:
        """ 从文档构建文档树 """
        # 查询文档信息
        result: IBlocks = self._client.queryDocFromDocID(root_id)
        if len(result) > 0:
            doc = result[0]
            # 获得笔记本节点
            node_notebook = self._addNotebookNode(id=doc['box'], name=self._notebooks.id2name(doc['box']))

            # 打印文档可读路径
            print(f"{root_id}: {node_notebook.data.content}{doc['hpath']}")

            # 获得文档路径
            paths, _, depth = self._parseDocPath(node_notebook, doc['path'], doc['hpath'])

            # 构建该文档的上级节点
            node_parent = node_notebook
            for i in range(1, depth - 1):
                result = self._client.queryDocFromDocID(paths[i])
                if len(result) > 0:
                    parent_doc = result[0]
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
            docs: IBlocks = self._client.querySubdocsFromDocID(doc['id'])

            # 通过查询结果构造文档树
            self._buildSubTreeFromDocList(
                node_default=node_parent,
                node_notebook=node_notebook,
                docs=docs,
            )

    def _buildBlockTreeFromBlockIDs(self, block_ids: t.List[str]) -> None:
        """ 从块 ID 列表构建块树 """
        for block_id in block_ids:
            breadcrumbs = self._client.getBlockBreadcrumb(block_id)
            if len(breadcrumbs) > 0:
                parent_id = breadcrumbs[0][0]
                for i in range(1, len(breadcrumbs)):
                    block = breadcrumbs[i]
                    node_parent = self.id2node(parent_id)
                    if node_parent is not None:
                        self._addNode(
                            node_parent=node_parent,
                            id=block[0],
                            data=Data(
                                content=block[1]
                            ),
                        )
                        parent_id = block[0]

    def _buildBlockTreeFromNotebookID(self, box: str) -> None:
        """ 从笔记本构建块树 """

        # 使用 SQL 查询所有叶子块的块 ID
        block_ids = self._client.queryBlocksFromNotebookID(box)

        # 构建块树
        self._buildBlockTreeFromBlockIDs(block_ids)

    def _buildBlockTreeFromDocID(self, root_id: str) -> None:
        """ 从文档构建块树 """

        # 使用 SQL 查询所有叶子块的块 ID
        block_ids = self._client.queryBlocksFromDocID(root_id)

        # 构建块树
        self._buildBlockTreeFromBlockIDs(block_ids)
