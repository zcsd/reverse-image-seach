# =============================================================================
# File name: app.py
# Author: Zichun
# Date created: 2022/08/10
# Python Version: 3.10
# Description:
#    This is the main file for the image search application.
#    It contains the main function and the main loop.
#    The main loop is responsible for the following:
#       - Initializing the application.
#       - Loading the image search engine.
#       - Handle real-time image search request.
# How to run:
#    python app.py
# =============================================================================

from datetime import datetime
from configparser import ConfigParser

from gevent.pywsgi import WSGIServer
from flask import Flask, jsonify, request
from flask_cors import CORS

from searcher.searcher import Searcher
from utils.image_util import base64_to_pil

collection_name = "imagenet_resnet_50_norm" # change here

app = Flask(__name__)

@app.route('/')
def index():
    # check AI server status
    entities_num = image_searcher.get_numer_of_entities()

    cpu = "Intel i5-9600K @ 3.70GHz, 6 cores"
    memory = "32GB"
    gpu = "NONE"
    
    if (isinstance(entities_num, int) and entities_num > 0):
        return jsonify({"ok": True, "entities_num": str(entities_num), "cpu": cpu, "memory": memory, "gpu": gpu})
    else:
        return jsonify({'ok': False})

@app.route("/cbir/", methods=['GET', 'POST'])
def cbir():
    if request.method == 'POST':
        data = request.json
        if data["key"] == "demo1":
            print('Valid Key.')
            img = base64_to_pil(data["image"])
            results = image_searcher.search(img, 6)

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S_%f")
            img.save("image_search/data/upload/" + timestamp +".JPEG") 
            print('An uploaded image saved.')

            image_base_url = cfg.get('url', 'image_base')
            
            resp = jsonify({'ok':True,
                    'image1': image_base_url + results[0].label.replace("@", "/"),
                    'image2': image_base_url + results[1].label.replace("@", "/"),
                    'image3': image_base_url + results[2].label.replace("@", "/"),
                    'image4': image_base_url + results[3].label.replace("@", "/"),
                    'image5': image_base_url + results[4].label.replace("@", "/"),
                    'result': "特征提取耗时：{} 毫秒, 搜索耗时: {} 毫秒".format(results[5].embedding_time, results[5].search_time)})
        else:
            print('Invalid Key.')
            resp = jsonify({'ok':False, 'result':'密钥不合法'})
        return resp
    else:
        return 'Invalid Method.\n'

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('image_search/conf/config.ini')

    image_searcher = Searcher(cfg.get('vector_server', 'host'), 
                          cfg.get('vector_server', 'port'),
                          collection_name)

    CORS(app, resources=r'/*')

    http_server = WSGIServer((cfg.get('http_server', 'host'), 
                            cfg.getint('http_server', 'port')),
                            app)

    print('Web server started at port {}.'.format(cfg.getint('http_server', 'port')))
    http_server.serve_forever() 
