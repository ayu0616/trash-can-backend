import random
from collections import Counter, defaultdict, deque
from typing import Callable

import MeCab
from nltk import ngrams


class MDicItem:
    def __init__(self) -> None:
        self.words: list[str] = []
        self.weights: list[int | float] = []


class MDicItem2:
    def __init__(self) -> None:
        self.words: list[tuple[str, ...]] = []
        self.weights: list[int | float] = []


class Marcov:
    __BEGIN__ = "__BEGIN__"
    __END__ = "__END__"

    def __init__(self, sentences: list[str] | None = None) -> None:
        self.trained = False
        if sentences:
            self.train(sentences)

    def train(self, sentences: list[str], weight_controler: Callable[[int], int | float] = lambda x: x):
        wakati = MeCab.Tagger("-Owakati")
        wakati_res: list[list[str]] = [[self.__BEGIN__] + wakati.parse(s).split() + [self.__END__] for s in sentences]
        trigrams: list[tuple[str, str, str]] = []
        for res in wakati_res:
            trigrams.extend(ngrams(res, 3))
        cnt = Counter(trigrams)

        self.m_dic: defaultdict[tuple[str, str], MDicItem] = defaultdict(MDicItem)
        for k, v in cnt.items():
            pre_words, next_word = k[:2], k[2]
            self.m_dic[pre_words].words.append(next_word)
            self.m_dic[pre_words].weights.append(weight_controler(v))

        begin_words_dic: defaultdict[str, int] = defaultdict(int)
        for k, v in cnt.items():
            if k[0] == self.__BEGIN__:
                next_word = k[1]
                begin_words_dic[next_word] += v

        self.begin_words = [k for k in begin_words_dic.keys()]
        self.begin_weights = [weight_controler(v) for v in begin_words_dic.values()]
        self.trained = True

    def generate(self, condition: Callable[[str], bool] | None = None) -> str:
        if not self.trained:
            raise Exception("Not trained yet.")
        begin_word = random.choices(self.begin_words, weights=self.begin_weights, k=1)[0]
        sentences: list[str] = [self.__BEGIN__, begin_word]
        while True:
            pre_words: tuple[str, str] = (sentences[-2], sentences[-1])
            next_word = random.choices(self.m_dic[pre_words].words, weights=self.m_dic[pre_words].weights, k=1)[0]
            if next_word == self.__END__:
                break
            sentences.append(next_word)
        text: str = "".join(sentences[1:])
        if condition:
            if not condition(text):
                return self.generate(condition)
        if not self.__check_bracket(text):
            return self.generate(condition)
        return text

    def generate_n(self, n: int, condition: Callable[[str], bool] | None = None):
        return [self.generate(condition) for _ in range(n)]

    def __check_bracket(self, s: str):
        """
        括弧の対応を確認する
        対応が取れていればTrue、取れていなければFalseを返す
        """
        STARTS = ("「", "（", "(", "『")
        ENDS = ("」", "）", ")", "』")
        q: deque[str] = deque()
        for char in s:
            for i in range(len(STARTS)):
                if char == STARTS[i]:
                    q.append(char)
                    break
                elif char == ENDS[i]:
                    if len(q) == 0:
                        return False
                    if q.pop() != STARTS[i]:
                        return False
                    break
        return len(q) == 0


class Marcov2(Marcov):
    __BEGIN__ = "__BEGIN__"
    __END__ = "__END__"

    def __init__(self, sentences: list[str] | None = None) -> None:
        self.trained = False
        if sentences:
            self.train(sentences)

    def train(self, sentences: list[str], weight_controler: Callable[[int], int | float] = lambda x: x):
        wakati = MeCab.Tagger("-Owakati")
        wakati_res: list[list[str]] = [[self.__BEGIN__] + wakati.parse(s).split() + [self.__END__] for s in sentences]
        grams: list[tuple[str, ...]] = []
        for res in wakati_res:
            grams.extend(ngrams(res, 5))
        cnt = Counter(grams)

        self.m_dic: defaultdict[tuple[str, ...], MDicItem2] = defaultdict(MDicItem2)
        for k, v in cnt.items():
            pre_words, next_word = k[:3], k[3:]
            self.m_dic[pre_words].words.append(next_word)
            self.m_dic[pre_words].weights.append(weight_controler(v))

        begin_words_dic: defaultdict[tuple[str, ...], int] = defaultdict(int)
        for k, v in cnt.items():
            if k[0] == self.__BEGIN__:
                next_word = k[1:3]
                begin_words_dic[next_word] += v

        self.begin_words = [k for k in begin_words_dic.keys()]
        self.begin_weights = [weight_controler(v) for v in begin_words_dic.values()]
        self.trained = True

    def generate(self, condition: Callable[[str], bool] | None = None) -> str:
        if not self.trained:
            raise Exception("Not trained yet.")
        begin_word = random.choices(self.begin_words, weights=self.begin_weights, k=1)[0]
        sentences: list[str] = [self.__BEGIN__, *begin_word]
        while True:
            pre_words: tuple[str, ...] = (sentences[-3], sentences[-2], sentences[-1])
            next_word = random.choices(self.m_dic[pre_words].words, weights=self.m_dic[pre_words].weights, k=1)[0]
            sentences.append(next_word[0])
            if next_word[1] == self.__END__:
                break
        text = "".join(sentences[1:])
        if condition:
            if not condition(text):
                return self.generate(condition)
        if not self.__check_bracket(text):
            return self.generate(condition)
        return text

    def generate_n(self, n: int, condition: Callable[[str], bool] | None = None):
        return [self.generate(condition) for _ in range(n)]

    def __check_bracket(self, s: str):
        """
        括弧の対応を確認する
        対応が取れていればTrue、取れていなければFalseを返す
        """
        STARTS = ("「", "（", "(", "『")
        ENDS = ("」", "）", ")", "』")
        q: deque[str] = deque()
        for char in s:
            for i in range(len(STARTS)):
                if char == STARTS[i]:
                    q.append(char)
                    break
                elif char == ENDS[i]:
                    if len(q) == 0:
                        return False
                    if q.pop() != STARTS[i]:
                        return False
                    break
        return len(q) == 0
