from flask import Flask, jsonify, request

import psychological
import settings
from generator import Generator

app = Flask(__name__)


@app.route("/sommelier/")
def sommelier():
    is_chaos = request.args.get("chaos", "false") == "true"
    shuffle_year = request.args.get("shuffle_year", "false") == "true"
    generator = Generator(is_chaos=is_chaos)
    sentences = [generator.generate(shuffle_year=shuffle_year) for _ in range(settings.N_SENTENCES)]
    return jsonify(sentences)


@app.route("/psychological_test")
def psychological_test():
    data = psychological.generate_n(25)
    return jsonify(data)


if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=3000)
    app.run(host="0.0.0.0", port=3000)
