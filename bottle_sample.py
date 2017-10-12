from bottle import route, run
from bottle import get, post, request,template

import json
import pymongo
from string import Template
from html import escape
from pymongo import MongoClient

# MongoDBのデータベースtestdbにコレクションartistを作成
client = MongoClient()
db = client.testdb
collection = db.artist

@route("/search",method ="GET")
def serach():
    name = request.forms.get('name')
    alias_name = request.forms.get("alias_name")
    tag = request.forms.get("tag")
    name = "" if name is None else name
    alias_name = "" if alias_name is None else alias_name
    tag = "" if tag is None else tag


    return '''
    <form action="/search" method="post">
    <br>
    name: <input name="name" type="text" value="{name}"/>
    <br>
    alias_name: <input name="alias_name" type="text" value="{alias_name}"/>
    <br>
    tag: <input name="tag" type="text" value="{tag}"/>
    <br>
    <input value="Search" type="submit" />
    </form>
    '''.format(name=name,
               alias_name=alias_name,
               tag=tag)



@route('/search', method='POST')  # or @post('/post')
def do_search():
    template_result = Template('''
        <hr />
        ($index件目/全$total件)<br />
        〔名前〕$name<br />
        〔別名〕$aliases<br />
        〔活動場所〕$area<br />
        〔タグ〕$tags<br />
        〔レーティング〕$rating<br />
        ''')



    name = request.forms.name
    alias_name = request.forms.alias_name
    tag = request.forms.tag

    print(name)
    print(alias_name)
    print(tag)
    condition = {}
    if len(name)>0:
        condition["name"] = name
    if len(alias_name) > 0:
        condition["aliases"] = {"$elemMatch": {"name": alias_name}}
    if len(tag) > 0:
        condition["tags"] = {"$elemMatch": {"value": tag}}

    docs = collection.find(condition).limit(25)
    print(docs)
    total = docs.count()
    print(total)
    contents = ""

    dict_template={}
    for i,doc in enumerate(docs, start = 1):
        # 結果表示部分のテンプレート用辞書に内容をセット
        dict_template['index'] = i
        dict_template['total'] = total
        dict_template['name'] = escape(doc['name'])

        if 'aliases' in doc:
            dict_template['aliases'] = \
                ','.join(escape(alias['name']) for alias in doc['aliases'])
        else:
            dict_template['aliases'] = '(データなし)'

        if 'area' in doc:
            dict_template['area'] = escape(doc['area'])
        else:
            dict_template['area'] = '(データなし)'

        if 'tags' in doc:
            dict_template['tags'] = \
                ','.join(escape(tag['value']) for tag in doc['tags'])
        else:
            dict_template['tags'] = '(データなし)'

        if 'rating' in doc:
            dict_template['rating'] = doc['rating']['count']
        else:
            dict_template['rating'] = '(データなし)'

        # 結果表示部分のテンプレート適用
        contents += template_result.substitute(dict_template)

    return (contents)



run(host="localhost", port=8080, dubug=True)
