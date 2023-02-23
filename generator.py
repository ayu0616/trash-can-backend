import random
import re
from collections import Counter, defaultdict
from itertools import product

import MeCab
from nltk import ngrams

import settings

__BEGIN__ = "__BEGIN__"
__END__ = "__END__"

__NOUN__ = "名詞"
__VERB__ = "動詞"
__ADJECTIVE__ = "形容詞"

NOUN_KIND = ["一般", "数", "形容詞語幹", "形容動詞語幹", "固有名詞", "サ変接続"]
EXCERCISES = ["未然形", "連用形", "終止形", "連体形", "仮定形", "命令形", "基本形", "連用テ接続", "連用タ接続", "ガル接続"]


class MDicItem:
    def __init__(self) -> None:
        self.words: list[str] = []
        self.weights: list[int] = []


class Generator:
    def __init__(self, is_chaos=False) -> None:
        self.is_chaos = is_chaos

        words, self.word_cnt = self.__load_txt_file(settings.TXT_FILE_PATH)

        self.__control_fraq_word_cnt()  # 出現頻度の調整

        grams: list[tuple[str, ...]] = []
        for w in words:
            grams.extend(ngrams(w, settings.N_GRAM))
        cnt = Counter(grams)

        self.m_dic: defaultdict[tuple[str, ...], MDicItem] = defaultdict(MDicItem)
        for k, v in cnt.items():  # type: ignore
            pre_words, next_word = k[:-1], k[-1]
            self.m_dic[pre_words].words.append(next_word)  # type: ignore
            self.m_dic[pre_words].weights.append(v**settings.FREQ_CONTROL)  # type: ignore

        begin_words_dic: defaultdict[tuple[str], int] = defaultdict(int)

        for k, v in cnt.items():  # type: ignore
            if k[0] == __BEGIN__:
                next_word = k[1:]  # type: ignore
                begin_words_dic[next_word] += v  # type: ignore

        self.begin_words = [k for k in begin_words_dic.keys()]
        self.begin_weights = [v for v in begin_words_dic.values()]

    def __load_txt_file(self, file_path: str):
        t = MeCab.Tagger()
        words: list[list[str]] = []
        word_cnt: defaultdict[str, defaultdict[str, defaultdict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        with open(file_path, "r") as f:
            for line in f:
                res_lines: list[str] = t.parse(line).replace("\t", ",").splitlines()
                res = [r.split(",") for r in res_lines if r != "EOS"]
                if self.is_chaos:
                    for r in res:
                        r1 = r[1]
                        if r1 == __NOUN__ and r[0] not in ["年"]:
                            for k in NOUN_KIND:
                                if k in r[2:]:
                                    word_cnt[__NOUN__][k][r[0]] += 1
                                    r[0] = f"{__NOUN__}+{k}"
                                    break
                        elif r1 == __VERB__:
                            for k in EXCERCISES:
                                if k in r[2:] and r[2] != "接尾" and "サ変・スル" not in r[2:]:
                                    last_nn = "+ん終わり" if r[0][-1] == "ん" else ""
                                    godan = "+五段" if [1 for v in r[2:] if "五段" in v] else ""
                                    word_cnt[__VERB__][f"{k}{last_nn}{godan}"][r[0]] += 1
                                    r[0] = f"{__VERB__}+{k}{last_nn}{godan}"
                                    break
                        elif r1 == __ADJECTIVE__:
                            for k in EXCERCISES:
                                if k in r[2:] and r[2] == "自立":
                                    word_cnt[__ADJECTIVE__][k][r[0]] += 1
                                    r[0] = f"{__ADJECTIVE__}+{k}"
                                    break
                li = [__BEGIN__] + [r[0] for r in res] + [__END__]
                words.append(li)
        return words, word_cnt

    def __control_fraq_word_cnt(self):
        "word_cntの出現頻度を制御する"
        for v1 in self.word_cnt.values():
            for v2 in v1.values():
                for k, v in v2.items():
                    v2[k] = v**settings.FREQ_CONTROL

    def generate(self, shuffle_year=False):
        begin_word = random.choices(self.begin_words, weights=self.begin_weights, k=1)[0]
        sentences: list[str] = [__BEGIN__, *begin_word]
        while True:
            pre_words = tuple(sentences[-(settings.N_GRAM - 1) :])
            next_word = random.choices(self.m_dic[pre_words].words, weights=self.m_dic[pre_words].weights, k=1)[0]
            if next_word == __END__:
                break
            sentences.append(next_word)

        if self.is_chaos:
            for i in range(len(sentences)):
                for k in NOUN_KIND:
                    if f"{__NOUN__}+{k}" == sentences[i]:
                        sentences[i] = random.choices(
                            list(self.word_cnt[__NOUN__][k].keys()),
                            weights=list(self.word_cnt[__NOUN__][k].values()),
                            k=1,
                        )[0]
                        break
                for k in EXCERCISES:
                    for op in product([0, 1], repeat=2):
                        k_op = k + "".join([["+ん終わり", "+五段"][i] * op[i] for i in range(len(op))])
                        if f"{__VERB__}+{k_op}" == sentences[i]:
                            sentences[i] = random.choices(
                                list(self.word_cnt[__VERB__][k_op].keys()),
                                weights=list(self.word_cnt[__VERB__][k_op].values()),
                                k=1,
                            )[0]
                            break
                    if f"{__ADJECTIVE__}+{k}" == sentences[i]:
                        sentences[i] = random.choices(
                            list(self.word_cnt[__ADJECTIVE__][k].keys()),
                            weights=list(self.word_cnt[__ADJECTIVE__][k].values()),
                            k=1,
                        )[0]
                        break
        text: str = "".join(sentences[1:])
        if shuffle_year:
            text = re.sub(r"\d{4}年([^代])", lambda x: f"{random.randint(1900, 2022)}年{x[1]}", text)
        return text


def main():
    generator = Generator(is_chaos=True)
    for i in range(20):
        text = generator.generate()
        print("{:02}. {}".format(i + 1, text))


if __name__ == "__main__":
    main()
