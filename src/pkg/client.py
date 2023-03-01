# 访问思源笔记服务的客户端
import typing as t

from .api import API
from .notebook import Notebooks

IDoc = t.Dict[str, str]
IDocs = t.List[IDoc]


class Client(object):
    """
    思源客户端
    """

    def __init__(
        self,
        token="",
        host="localhost",
        port="6806",
        ssl=False,
        proxies=None,
    ):
        self._api = API(
            token=token,
            host=host,
            port=port,
            ssl=ssl,
            proxies=proxies,
        )

    def getNotebooks(self) -> Notebooks:
        """ 获取所有笔记本 """
        response = self._api.post(url=self._api.url.lsNotebooks)
        notebooks = Notebooks.fromList(response.body['data']['notebooks'])
        return notebooks

    def queryDocsFromBox(self, box: str) -> IDocs:
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
        return response.body['data']

    def queryDocFromDocID(self, root_id: str) -> IDocs:
        """ 通过文档 ID 查询文档 """
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
        return response.body['data']

    def querySubdocsFromDocID(self, id: str) -> IDocs:
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
                        b.path LIKE '%/{id}/%'
                        AND b.type = 'd'
                    ORDER BY
                        LENGTH(b.path),
                        b.path
                """
            },
        )
        return response.body['data']
