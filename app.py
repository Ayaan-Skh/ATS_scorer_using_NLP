from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"


@app.route('/scrape_jd',methods=["POST"])
def scrape_jd():
    return "<input id=link type=text/> <button>Get description</button>"

if __name__ == '__main__':
    app.run(debug=True,port=8000)