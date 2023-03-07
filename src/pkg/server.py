# -*- coding: utf-8 -*-
# Web 服务器

import json
import typing as t

from flask import Flask, request

from .fts import FTS
from .tree import Tree
from .extractor import Extractor


class Server(object):
    def __init__(
        self,
        path_index: str,  # 索引文件目录路径
        path_tree_file_with_full_keys: str,  # 带有完整关键词的树文件路径
        host: str = 'localhost',  # 服务器主机
        port: int = 5000,  # 服务器端口
        defug: bool = True,  # 调试模式
    ):
        self._path_index = path_index
        self._path_tree_file_with_full_keys = path_tree_file_with_full_keys
        self._host = host
        self._port = port
        self._defug = defug
        self._app = Flask(__name__)
        self.init()

    def init(self):
        # 加载索引文件
        self._fts = FTS(
            index_dir=self._path_index
        )
        self._fts.openIndex()

        # 加载树文件
        with open(self._path_tree_file_with_full_keys, 'r') as f:
            self._tree = Tree.fromDict(json.loads(f.read()))

        # 加载成分句法分析器
        self._extractor = Extractor()

        # 注册路由
        self._app.add_url_rule(
            rule='/query',
            view_func=self.query,
            methods=['GET'],
        )
        # @self._app.route('/query', methods=['GET'])
        # def query() -> t.Dict[str, t.Any]:
        #     q = request.args.get('q')
        #     return self.query(q)

    def query(self) -> t.Dict[str, t.Any]:
        q = request.args.get('q')
        phrases, words = self._extractor.classify(set(q.split()))
        query = f"{' OR '.join(phrases)} OR ({' AND '.join(words)})"
        response = {
            'phrases': list(phrases),
            'words': list(words),
            'query': query,
            'results': [],
        }
        with self._fts.searcher as s:
            results = s.search(self._fts.parse(query).query)
            for result in results:
                node_id = result['id']
                node = self._tree.id2node(node_id)
                breadcrumbs = self._tree.getBreadcrumb(node_id)
                response['results'].append({
                    'node': {
                        'id': node.id,
                        'url': f"siyuan://blocks/{node.id}",
                        'data': node.data.__dict__(),
                    },
                    'breadcrumbs': list(map(
                        lambda breadcrumb: {
                            'id': breadcrumb.id,
                            'url': f"siyuan://blocks/{breadcrumb.id}",
                            'data': breadcrumb.data.__dict__(),
                        },
                        breadcrumbs,
                    ))
                })
        return response

    def run(self):
        self._app.run(
            host=self._host,
            port=self._port,
            debug=self._defug,
        )
