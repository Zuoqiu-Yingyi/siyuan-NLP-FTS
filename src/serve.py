# -*- coding: utf-8 -*-
from pkg.server import Server

if __name__ == '__main__':
    root_id = '20220909082530-85ixym4'  # 课程/人工智能与机器学习
    path_root = './data/prod'  # 数据目录
    path_tree_dir = f'{path_root}/tree'  # 节点树目录
    path_tree_file = f'{path_tree_dir}/{root_id}.json'  # 节点树文件
    path_tree_file_with_keys = f'{path_tree_dir}/{root_id}-keys.json'  # 提取了关键字的节点树文件
    path_tree_file_with_full_keys = f'{path_tree_dir}/{root_id}-full-keys.json'  # 继承了上级节点关键字的树文件
    path_index = f'{path_root}/index/{root_id}/'  # 索引文件保存目录

    server = Server(
        path_index=path_index,
        path_tree_file_with_full_keys=path_tree_file_with_full_keys,
    )

    server.run()
