pymason
=======

Builder and parser for the [Mason hypermedia
format](https://github.com/JornWildt/Mason), which is JSON compatible but
defines how hypermedia controls can be added to JSON objects.

Parsing mason documents
-----------------------

```python
>>> import json
>>> location = 'http://my-site.com/messages/17'
>>> masondoc = {
...     'id': 17,
...     'content': 'Hello!',
...     '@namespaces': {
...         'msg': {
...             'name': 'http://example.org/messages/reltypes#delete-message'
...         }
...     },
...     '@controls': {
...         'self': {
...             'href': '/messages/17'
...         },
...         'msg:': {
...             'href': '/messages/17',
...             'method': 'DELETE'
...         }
...     }
... }
>>>
>>> from mason.parser import parse
>>> doc = parse(location, masondoc)
>>> doc.root
Object {'content': 'Hello!', 'id': 17}
>>> doc.root.controls.keys()
['self', 'http://example.org/messages/reltypes#delete-message']
>>> doc.root.controls['http://example.org/messages/reltypes#delete-message']
Control {'href': 'http://my-site.com/messages/17', 'method': 'DELETE'}
```

Building mason documents
------------------------

```python
>>> from mason.builder import Builder, Document, Object
>>> import json
>>>
>>> doc = Document()
>>> doc.root = Object('/messages/17', {'id': 17, 'content': 'Hello!'})
>>> doc.root.controls.add('http://example.org/messages/reltypes#delete-message',
...     '/messages/17', method='DELETE')
>>>
>>> builder = Builder({'msg': 'http://example.org/messages/reltypes#delete-message'})
>>> masondoc = builder.build(doc)
>>> print json.dumps(masondoc, indent=4)
{
    "content": "Hello!",
    "@namespaces": {
        "msg": {
            "name": "http://example.org/messages/reltypes#delete-message"
        }
    },
    "id": 17,
    "@controls": {
        "self": {
            "href": "/messages/17"
        },
        "msg:": {
            "href": "/messages/17",
            "method": "DELETE"
        }
    }
}
```
