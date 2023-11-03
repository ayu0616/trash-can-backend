from flask import Flask, jsonify, request

import psychological
import settings
from generator import Generator

app = Flask(__name__)


@app.route("/sommelier/")
def sommelier():
    is_chaos = request.args.get("chaos", "false") == "true"
    shuffle_year = request.args.get("shuffle_year", "false") == "true"
    gram_n = request.args.get("gram_n", 3, type=int)
    generator = Generator(is_chaos=is_chaos, gram_n=gram_n)
    sentences = [generator.generate(shuffle_year=shuffle_year) for _ in range(settings.N_SENTENCES)]
    return jsonify(sentences)


@app.route("/psychological_test")
def psychological_test():
    data = psychological.generate_n(25)
    return jsonify(data)


if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=3000)
    app.run(host="0.0.0.0", port=3001)
