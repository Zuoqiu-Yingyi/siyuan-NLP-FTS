# -*- coding: utf-8 -*-
# 关键短语提取器
import typing as t
import hanlp


class Extractor(object):
    """
    关键短语提取器
    """

    def __init__(
        self,
        tags: t.Set[str] = {
            'NP',  # 名词短语

            'NN',  # 其他名词
            'NR',  # 专有名词
            'NT',  # 时间名词

            'VCD',  # 复合动词
            'VP',  # 动词短语

            'VV',  # 其他动词
        },  # 句子成分
        model: str = hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ERNIE_GRAM_ZH,  # 预训练模型
        max_key_word_count: int = 8,  # 构成关键短语的关键词最大数量
    ):
        self._tags = tags
        self._model = model
        self._max_key_word_count = max_key_word_count
        self._component = hanlp.load(self._model)  # 预训练组件

    def __call__(
        self,
        sentences: t.Set[str],  # 待提取关键短语的多个语句
    ) -> t.Set[str]:
        return self.handle(sentences, self._tags)

    def handle(
        self,
        sentences: t.Set[str],  # 待提取关键短语的多个语句
        tags: t.Set[str],  # 句子成分
    ) -> t.Set[str]:
        results_con = self.parse(sentences)
        key_phrases = self.filter(results_con, tags)
        return key_phrases

    def parse(self, sentences: t.Set[str]):
        results = self._component(list(sentences))
        results_con = results['con']
        return results_con

    def filter(
        self,
        results_con,
        tags: t.Set[str],
    ) -> t.Set[str]:
        key_phrases = set()
        for result_con in results_con:
            for subtree in result_con.subtrees(lambda t: t.label() in tags):
                keywords = subtree.leaves()
                if len(keywords) <= self._max_key_word_count:
                    key_phrases.add(''.join(keywords))

        return key_phrases

    def classify(
        self,
        sentences: t.Set[str],  # 待提取关键短语的多个语句
    ) -> t.Tuple[t.Set[str], t.Set[str]]:
        results_con = self.parse(sentences)
        key_phrases = self.filter(results_con, {
            'NP',  # 名词短语
            'VCD',  # 复合动词
            'VP',  # 动词短语
        })
        key_words = self.filter(results_con, {
            'NN',  # 其他名词
            'NR',  # 专有名词
            'NT',  # 时间名词
        })
        return key_phrases, key_words
