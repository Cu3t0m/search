from flask import *
import libs.search as search

app = Flask('app')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/search')
def main_search():
    query = request.args.get("q")
    source = request.args.get("src")
    if source == None:
        source = "google"

    res = search.request(source, query)
    #return res
    return render_template("stemp.html", results=res)

@app.route('/api/v1/search')
def api_search():
    query = request.args.get("q")
    source = request.args.get("src")
    if source == None:
        source = "google"

    res = search.request(source, query)
    return res


@app.route('/api/v1/sidebar')
def api_sidebar():
    query = request.args.get("q")
    res = search.sidebar(query)
    return res


@app.route('/api/v1/autocomplete')
def api_autocomplete():
    prompt = request.args.get("q")

    res = search.autocomplete(prompt)
    return res


app.run(host='0.0.0.0', port=8080)
