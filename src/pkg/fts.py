# -*- coding: utf-8 -*-
# 全文搜索 Full Text Search
from enum import Enum, unique
import typing as t
import os

from whoosh.filedb.filestore import FileStorage
from whoosh import fields
from whoosh import index
from whoosh import writing
from whoosh import qparser
from whoosh import query
from whoosh import searching


@unique
class Mode(Enum):
    """ 模式 """
    MANUAL = 0  # 手动
    INIT = 1  # 初始化索引目录
    OPEN = 2  # 打开存在的索引


class FTS(object):
    """
    全文搜索
    """

    def __init__(
        self,
        index_dir: str = "./data/index/",
        schema: fields.Schema = fields.Schema(
            id=fields.ID(
                stored=True,
                unique=True,
            ),
            keys=fields.KEYWORD(
                stored=True,
                commas=True,
                # sortable=True,
            ),
            content=fields.STORED,
        ),
        fieldname: str = 'keys',
        mode: Mode = Mode.MANUAL,
    ):
        self._index_dir = index_dir
        self._schema = schema
        self._fieldname = fieldname
        self._storage: FileStorage = FileStorage(index_dir)
        self._index: t.Optional[index.Index] = None
        self._writer: t.Optional[writing.IndexWriter] = None
        self._parser: t.Optional[qparser.QueryParser] = None
        self._query: t.Optional[query.Query] = None
        self._searcher: t.Optional[searching.Searcher] = None

        if mode == Mode.MANUAL:
            pass
        elif mode == Mode.INIT:
            self.initIndex()
        elif mode == Mode.OPEN:
            self.openIndex()

    def initIndex(self) -> 'FTS':
        """ 创建索引 """
        os.makedirs(self._index_dir, exist_ok=True)
        self._index = self._storage.create_index(self._schema)
        return self

    def openIndex(self) -> 'FTS':
        """ 打开索引 """
        self._index = self._storage.open_index()
        self._schema = self._index.schema
        return self

    @property
    def writer(self) -> writing.IndexWriter:
        """ 获取写入器 """
        if self._writer is None:
            self._writer = self._index.writer()
        return self._writer

    def add_document(self, **kw) -> 'FTS':
        """ 添加一条记录 """
        self.writer.add_document(**kw)
        return self

    def cancel(self) -> 'FTS':
        """ 取消写入 """
        self.writer.cancel()
        self._writer = None
        return self

    def commit(self) -> 'FTS':
        """ 提交写入 """
        self.writer.commit()
        self._writer = None
        return self

    @property
    def parser(self) -> qparser.QueryParser:
        """ 获取解析器 """
        if self._parser is None:
            self._parser = qparser.QueryParser(
                fieldname=self._fieldname,
                schema=self._schema,
            )
        return self._parser

    def parse(
        self,
        query: str,
    ) -> 'FTS':
        """ 解析查询 """
        self._query = self.parser.parse(query)
        return self

    @property
    def query(self) -> t.Optional[query.Query]:
        """ 获取查询器 """
        return self._query

    @property
    def searcher(self) -> searching.Searcher:
        """ 获取搜索器 """
        if self._searcher is not None and not self._searcher.is_closed:
            self._searcher.close()
        self._searcher = self._index.searcher()
        return self._searcher
