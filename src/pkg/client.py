# 访问思源笔记服务的客户端
import typing as t

from .api import API
from .notebook import Notebooks

IBlock = t.Dict[str, str]
IBlocks = t.List[IBlock]


class Client(object):
    """
    思源客户端
    """

    @classmethod
    def fromDict(cls, d: t.Dict[str, t.Any]) -> 'API':
        """ 从字典创建节点 """
        return cls(
            token=d['token'],
            host=d['host'],
            port=d['port'],
            ssl=d['ssl'],
            proxies=d['proxies'],
        )

    def __init__(
        self,
        token: str = "",
        host: str = "localhost",
        port: int = 6806,
        ssl: bool = False,
        proxies: t.Optional[t.Dict[str, str]] = None,
    ):
        self._api = API(
            token=token,
            host=host,
            port=port,
            ssl=ssl,
            proxies=proxies,
        )

    def __dict__(self) -> t.Dict[str, t.Any]:
        return self._api.__dict__()

    def getNotebooks(self) -> Notebooks:
        """ 获取所有笔记本 """
        response = self._api.post(url=self._api.url.lsNotebooks)
        notebooks = Notebooks.fromList(response.result['data']['notebooks'])
        return notebooks

    def queryDocsFromNotebookID(self, box: str) -> IBlocks:
        """ 通过笔记本 ID 查询笔记本下的所有文档 """
        response = self._api.post(
            url=self._api.url.sql,
            body={
                'stmt': f"""
                    SELECT
                        b.id, -- 文档 ID
                        b.box, -- 笔记本 ID
                        b.content, -- 文档标题
                        b.name, -- 命名
                        b.alias, -- 别名
                        b.memo, -- 备注
                        b.path, -- 文件路径
                        b.hpath -- 可读路径
                    FROM
                        blocks AS b
                    WHERE
                        b.box = '{box}'
                        AND b.type = 'd'
                    ORDER BY
                        LENGTH(b.path),
                        b.path
                """
            },
        )
        return response.result['data']

    def queryDocFromDocID(self, root_id: str) -> IBlocks:
        """ 通过文档 ID 查询单个文档 """
        response = self._api.post(
            url=self._api.url.sql,
            body={
                'stmt': f"""
                    SELECT
                        b.id, -- 文档 ID
                        b.box, -- 笔记本 ID
                        b.content, -- 文档标题
                        b.name, -- 命名
                        b.alias, -- 别名
                        b.memo, -- 备注
                        b.path, -- 文件路径
                        b.hpath -- 可读路径
                    FROM
                        blocks AS b
                    WHERE
                        b.id = '{root_id}'
                        AND b.type = 'd'
                """
            },
        )
        return response.result['data']

    def querySubdocsFromDocID(self, root_id: str) -> IBlocks:
        """ 通过文档 ID 查询文档下的所有子文档 """
        response = self._api.post(
            url=self._api.url.sql,
            body={
                'stmt': f"""
                    SELECT
                        b.id, -- 文档 ID
                        b.box, -- 笔记本 ID
                        b.content, -- 文档标题
                        b.name, -- 命名
                        b.alias, -- 别名
                        b.memo, -- 备注
                        b.path, -- 文件路径
                        b.hpath -- 可读路径
                    FROM
                        blocks AS b
                    WHERE
                        b.path LIKE '%/{root_id}/%'
                        AND b.type = 'd'
                    ORDER BY
                        LENGTH(b.path),
                        b.path
                """
            },
        )
        return response.result['data']

    def queryBlocksFromNotebookID(self, box: str) -> t.List[str]:
        """通过笔记本 ID 查询文档下的所有块 """
        response = self._api.post(
            url=self._api.url.sql,
            body={
                'stmt': f"""
                    SELECT
                        b.id -- 块 ID
                    FROM
                        blocks AS b
                    WHERE
                        b.box = '{box}'
                        AND b.content != ''
                        AND (
                            b.type = 'p'
                            OR b.type = 'h'
                        )
                    ORDER BY
                        LENGTH(b.path),
                        b.path,
                        LENGTH(b.subtype),
                        b.subtype DESC
                """
            },
        )
        return list(map(lambda block: block['id'], response.result['data']))

    def queryBlocksFromDocID(self, root_id: str) -> t.List[str]:
        """通过文档 ID 查询文档及其下级文档中的所有块 """
        response = self._api.post(
            url=self._api.url.sql,
            body={
                'stmt': f"""
                    SELECT
                        b.id -- 块 ID
                    FROM
                        blocks AS b
                    WHERE
                        b.path LIKE '%/{root_id}%'
                        AND b.content != ''
                        AND (
                            b.type = 'p'
                            OR b.type = 'h'
                        )
                    ORDER BY
                        LENGTH(b.path),
                        b.path,
                        LENGTH(b.subtype),
                        b.subtype DESC
                """
            },
        )
        return list(map(lambda block: block['id'], response.result['data']))
    
    def getBlockBreadcrumb(self, block_id: str) -> t.List[t.Tuple[str, str]]:
        """ 获取块的面包屑 """
        response = self._api.post(
            url=self._api.url.getBlockBreadcrumb,
            body={
                'id': block_id,
                'excludeTypes': [],
            },
        )
        return list(map(lambda block: (block['id'], block['name']), response.result['data']))
