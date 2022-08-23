#!/bin/python
from flask import Flask, jsonify, request, render_template, Response, json
from flask_bootstrap import Bootstrap

from Ticker import Ticker

import jsonpickle
import TickerImport
from RedisClient import RedisClient

app = Flask(__name__)
app.debug = True
bootstrap = Bootstrap()

print("beginning of appy.py now")
db = RedisClient()


@app.route('/', defaults={'path': ''}, methods=['PUT', 'GET', 'POST'])
@app.route('/<path:path>', methods=['PUT', 'GET', 'POST', 'DELETE'])
def home(path):
    return_string = ""
    print("the request method is " + request.method + " path is " + path)

    if request.method == 'PUT':
        print('in PUT')
        event = request.json
        print('event is %s ' % event)
        nextTicker = Ticker(**event)
        nextTicker.set_key()
        # event['updated'] = int(time.time())
        # db.hmset(path, event)
        db.write_ticker(nextTicker)
        return_string = jsonify(nextTicker.__dict__, 201)

    elif request.method == 'DELETE':
        return_status = db.delete(path)
        print("delete with path = " + path + " and status of " + str(return_status))
        return_string = jsonify(str(return_status), 201)

    elif request.method == 'GET':
        print("GET Method with path " + path)
        if path == 'search/':
            search_column = request.args.get("search_column")
            # print("search column is " + search_column)
            search_str = request.args.get("search_string")
            sort_by = request.args.get("sort_column")
            print("search string is " + search_str)
            ticker_search = "@" + str(search_column) + ":" + str(search_str) + "*"
            most_recent = request.args.get("most_recent")
            if most_recent is not None and most_recent == "true":
                ticker_search = ticker_search + " @mostrecent:{ true }"

            print("TickerSearch is " + ticker_search, flush=True)
            search_return = db.ft_search(ticker_search, sort_by)
            print("total number returned is " + str(search_return.total), flush=True)
            # print("page number " + str(len(search_return.docs)))
            # print("TickerReturn")
            # print(TickerReturn)
            # print("TickerReturn docs 0")
            # print("docs array 0 ", flush=True)
            # print(TickerReturn.docs[0], flush=True)
            # print("TickerReturn docs 0 id")
            # print(TickerReturn.docs[0].id, flush=True)
            # print("TickerReturn docs 0 json", flush=True)
            # print(TickerReturn.docs[0].json, flush=True)
            # print("TickerReturn docs 0 json tickershort", flush=True)
            ticker_results = db.process_index_search_results(search_return)
            return_string = jsonpickle.encode(ticker_results)
            # return_string = TickerResults
            print("final return string", flush=True)
            print(return_string, flush=True)
        # this is returning all the rows for the one ticker in the box
        elif path == 'oneticker/':
            get_ticker = request.args.get("ticker")
            print("reporting ticket is ", get_ticker)
            sort_by = request.args.get("sort_column")
            ticker_search = "@ticker:" + get_ticker
            print("TickerSearch is " + ticker_search)
            search_return = db.ft_search(ticker_search, sort_by)
            print("number returned is " + str(search_return.total))
            print("page number " + str(len(search_return.docs)))
            # print("TickerReturn")
            # print(TickerReturn)
            # print("TickerReturn docs 0")
            # print(TickerReturn.docs[0])
            # print("TickerReturn docs 0 id")
            # print(TickerReturn.docs[0].id)
            # print("TickerReturn.docs[0].json")
            # print(TickerReturn.docs[0].json)
            # print("TickerReturn docs 0 tickershort")
            # print(TickerReturn.docs[0].tickershort)

            ticker_results = db.process_index_search_results(search_return)
            return_string = jsonpickle.encode(ticker_results)
            print(return_string, flush=True)
        elif path == 'index':
            db.recreate_index()
            return_string = "Done"
        else:
            print("in the GET before call to index.html")
            response = app.send_static_file('index.html')
            response.headers['Content-Type'] = 'text/html'
            return_string = response
    elif request.method == 'POST':
        if path == 'upload-csv-file':
            get_directory = request.args.get("directory")
            print("loading files with this directory " + get_directory)
            TickerImport.load_directory(get_directory)
            return_string = "Done"
    return return_string


@app.after_request  # blueprint can also be app~~
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE'
    if response.headers['Content-Type'] != 'text/html':
        response.headers['Content-Type'] = 'application/json'
    return response


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    app.run(host='0.0.0.0')
