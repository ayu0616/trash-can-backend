import json
from typing import TypedDict

from marcov import Marcov


class Setting:
    res_body_min = 50
    res_body_max = 200

    option_n = 4

    json_path = "./data/crea_ok.json"


class Option(TypedDict):
    value: str
    result: str


class Data(TypedDict):
    question: str
    options: list[Option]


def generate_n(n: int):
    # データを読み込む
    with open(Setting.json_path, "r") as f:
        d: list[Data] = json.load(f)

    q_model = Marcov()  # 質問文のモデル
    op_model = Marcov()  # 選択肢のモデル
    res_s_model = Marcov()  # テスト結果の要約のモデル
    res_b_model = Marcov()  # テスト結果の本文のモデル
    questions: list[str] = []
    options: list[str] = []
    result_summaries: list[str] = []
    result_bodies: list[str] = []
    for d_item in d:
        questions.append(d_item["question"])
        d_options = d_item["options"]
        options.extend([op_item["value"] for op_item in d_options])
        result_summaries.extend([op_item["result"].splitlines()[0] for op_item in d_options])
        result_bodies.extend(["".join(op_item["result"].splitlines()[1:]) for op_item in d_options])

    q_model.train(questions)
    op_model.train(options)
    res_s_model.train(result_summaries)
    res_b_model.train(result_bodies)

    res = []
    for _ in range(n):
        q_text = q_model.generate(lambda x: x.endswith("がわかります。") and x.count("？") == 1)
        op_texts = op_model.generate_n(Setting.option_n)
        res_ss = res_s_model.generate_n(Setting.option_n)
        res_bs = res_b_model.generate_n(Setting.option_n, lambda x: Setting.res_body_min <= len(x) <= Setting.res_body_max)
        res.append({"question": q_text, "options": op_texts, "result_summaries": res_ss, "result_bodies": res_bs})
    return res


def main():
    # データを読み込む
    with open(Setting.json_path, "r") as f:
        d: list[Data] = json.load(f)

    q_model = Marcov()  # 質問文のモデル
    op_model = Marcov()  # 選択肢のモデル
    res_s_model = Marcov()  # テスト結果の要約のモデル
    res_b_model = Marcov()  # テスト結果の本文のモデル
    questions: list[str] = []
    options: list[str] = []
    result_summaries: list[str] = []
    result_bodies: list[str] = []
    for d_item in d:
        questions.append(d_item["question"])
        d_options = d_item["options"]
        options.extend([op_item["value"] for op_item in d_options])
        result_summaries.extend([op_item["result"].splitlines()[0] for op_item in d_options])
        result_bodies.extend(["".join(op_item["result"].splitlines()[1:]) for op_item in d_options])
    q_model.train(questions)
    op_model.train(options)
    res_s_model.train(result_summaries)
    res_b_model.train(result_bodies)

    q_text = q_model.generate(lambda x: x.endswith("がわかります。") and x.count("？") == 1)
    print(q_text, end="\n\n")
    print(*op_model.generate_n(Setting.option_n), sep="\n", end="\n\n")
    print(*res_s_model.generate_n(Setting.option_n), sep="\n", end="\n\n")
    print(*res_b_model.generate_n(Setting.option_n, lambda x: Setting.res_body_min <= len(x) <= Setting.res_body_max), sep="\n")


if __name__ == "__main__":
    main()
