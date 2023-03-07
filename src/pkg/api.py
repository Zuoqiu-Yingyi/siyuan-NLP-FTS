# -*- coding: utf-8 -*-
# 思源 API
import typing as t
import requests


class Result(object):
    def __init__(self, result):
        self.result = result
        self.code = result.get('code')
        self.msg = result.get('msg')
        self.data = result.get('data')


class APIError(RuntimeError):
    def __init__(
        self,
        response: requests.Response,
        result: Result,
        msg: str,
    ):
        self.response = response
        self.result = result
        self.msg = msg


def parse(request):
    def wrapper(*args, **kw) -> Result:
        response = request(*args, **kw)
        if response.status_code == 200:
            result = Result(response.json())
            if result.code == 0:
                return result
            else:
                raise APIError(
                    response=response,
                    result=result,
                    msg=result.msg,
                )
        else:
            raise requests.HTTPError(response)
    return wrapper


class URL:
    lsNotebooks = "/api/notebook/lsNotebooks"
    openNotebook = "/api/notebook/openNotebook"
    closeNotebook = "/api/notebook/closeNotebook"
    renameNotebook = "/api/notebook/renameNotebook"
    createNotebook = "/api/notebook/createNotebook"
    removeNotebook = "/api/notebook/removeNotebook"
    getNotebookConf = "/api/notebook/getNotebookConf"
    setNotebookConf = "/api/notebook/setNotebookConf"

    createDocWithMd = "/api/filetree/createDocWithMd"
    renameDoc = "/api/filetree/renameDoc"
    removeDoc = "/api/filetree/removeDoc"
    moveDoc = "/api/filetree/moveDoc"
    getHPathByPath = "/api/filetree/getHPathByPath"

    upload = "/api/asset/upload"

    insertBlock = "/api/block/insertBlock"
    prependBlock = "/api/block/prependBlock"
    appendBlock = "/api/block/appendBlock"
    updateBlock = "/api/block/updateBlock"
    deleteBlock = "/api/block/deleteBlock"
    getBlockBreadcrumb = "/api/block/getBlockBreadcrumb"

    setBlockAttrs = "/api/attr/setBlockAttrs"
    getBlockAttrs = "/api/attr/getBlockAttrs"

    sql = "/api/query/sql"

    exportMdContent = "/api/export/exportMdContent"

    bootProgress = "/api/system/bootProgress"
    version = "/api/system/version"
    currentTime = "/api/system/currentTime"

    def __init__(self, socket):
        self.lsNotebooks = socket + URL.lsNotebooks
        self.openNotebook = socket + URL.openNotebook
        self.closeNotebook = socket + URL.closeNotebook
        self.renameNotebook = socket + URL.renameNotebook
        self.createNotebook = socket + URL.createNotebook
        self.removeNotebook = socket + URL.removeNotebook
        self.getNotebookConf = socket + URL.getNotebookConf
        self.setNotebookConf = socket + URL.setNotebookConf
        self.createDocWithMd = socket + URL.createDocWithMd
        self.renameDoc = socket + URL.renameDoc
        self.removeDoc = socket + URL.removeDoc
        self.moveDoc = socket + URL.moveDoc
        self.getHPathByPath = socket + URL.getHPathByPath
        self.upload = socket + URL.upload
        self.insertBlock = socket + URL.insertBlock
        self.prependBlock = socket + URL.prependBlock
        self.appendBlock = socket + URL.appendBlock
        self.updateBlock = socket + URL.updateBlock
        self.deleteBlock = socket + URL.deleteBlock
        self.getBlockBreadcrumb = socket + URL.getBlockBreadcrumb
        self.setBlockAttrs = socket + URL.setBlockAttrs
        self.getBlockAttrs = socket + URL.getBlockAttrs
        self.sql = socket + URL.sql
        self.exportMdContent = socket + URL.exportMdContent
        self.bootProgress = socket + URL.bootProgress
        self.version = socket + URL.version
        self.currentTime = socket + URL.currentTime


class API(object):

    def __init__(
        self,
        token: str = '',
        host: str = 'localhost',
        port: int = 6806,
        ssl: bool = False,
        proxies: t.Optional[t.Dict[str, str]] = None,
    ):
        self._token = token
        self._host = host
        self._port = port
        self._ssl = ssl
        self._proxies = proxies

        self._protocol = ('https' if ssl else 'http')
        self._headers = {
            'Authorization': f'Token {self._token}',
        }
        self.socket = f'{self._protocol}://{self._host}:{self._port}'
        self.url = URL(self.socket)
        self._session = requests.Session()
        self._session.headers.update(self._headers)
        if proxies is not None:
            self._session.proxies.update(proxies)

    def __dict__(self) -> t.Dict[str, t.Any]:
        return {
            'token': self._token,
            'host': self._host,
            'port': self._port,
            'ssl': self._ssl,
            'proxies': self._proxies,
        }

    @parse
    def post(self, url, body=None):
        if body is None:
            return self._session.post(url)
        else:
            return self._session.post(url, json=body)

    @parse
    def upload(self, path: str, files: list):
        return self._session.post(
            self.url.upload,
            data={
                'assetsDirPath': path,
            },
            files=[('file[]', file) for file in files]
        )
