from mason.builder import Builder, Document, Object
from mason.parser import parse


class TestBuild(object):
    def test_simple(self):
        doc = Document()
        doc.root = Object('/messages/17', {'id': 17, 'content': 'Hello!'})
        res = Builder().build(doc)
        assert res == {
            'id': 17,
            'content': 'Hello!',
            '@controls': {
                'self': {
                    'href': '/messages/17'
                }
            }
        }

    def test_with_control(self):
        doc = Document()
        doc.root = Object('/messages/17', {'id': 17, 'content': 'Hello!'})
        doc.root.controls.add('http://example.org/messages/reltypes#delete-message',
                '/messages/17', method='DELETE')
        res = Builder().build(doc)
        assert res == {
            'id': 17,
            'content': 'Hello!',
            '@controls': {
                'self': {
                    'href': '/messages/17'
                },
                'http://example.org/messages/reltypes#delete-message': {
                    'href': '/messages/17',
                    'method': 'DELETE'
                }
            }
        }

    def test_with_control_and_namespace(self):
        namespace = 'http://example.org/messages/reltypes#'
        delete_message_rel = namespace + 'delete-message'

        doc = Document()
        doc.root = Object('/messages/17', {'id': 17, 'content': 'Hello!'})
        doc.root.controls.add(delete_message_rel, '/messages/17', method='DELETE')

        res = Builder({'msg': namespace}).build(doc)
        expected = {
            'id': 17,
            'content': 'Hello!',
            '@namespaces': {
                'msg': {
                    'name': 'http://example.org/messages/reltypes#'
                }
            },
            '@controls': {
                'self': {
                    'href': '/messages/17'
                },
                'msg:delete-message': {
                    'href': '/messages/17',
                    'method': 'DELETE'
                }
            }
        }
        assert res == expected


class TestParser(object):
    def test_simple(self):
        doc = parse('http://example.org/messages/17', {
            'id': 17,
            'content': 'Hello!',
            '@controls': {
                'self': {
                    'href': '/messages/17'
                }
            }
        })
        assert doc.root['id'] == 17
        assert doc.root['content'] == 'Hello!'
        assert doc.root.controls['self'].href == 'http://example.org/messages/17'

    def test_with_control(self):
        doc = parse('http://example.org/messages/17', {
            'id': 17,
            'content': 'Hello!',
            '@controls': {
                'self': {
                    'href': '/messages/17'
                },
                'http://example.org/messages/reltypes#delete-message': {
                    'href': '/messages/17',
                    'method': 'DELETE'
                }
            }
        })
        assert doc.root['id'] == 17
        assert doc.root['content'] == 'Hello!'
        assert doc.root.controls['self'].href == 'http://example.org/messages/17'
        assert doc.root.controls['http://example.org/messages/reltypes#delete-message'].href == 'http://example.org/messages/17'
        assert doc.root.controls['http://example.org/messages/reltypes#delete-message'].method == 'DELETE'

    def test_with_control_and_namespace(self):
        doc = parse('http://example.org/messages/17', {
            'id': 17,
            'content': 'Hello!',
            '@namespaces': {
                'msg': {
                    'name': 'http://example.org/messages/reltypes#'
                }
            },
            '@controls': {
                'self': {
                    'href': '/messages/17'
                },
                'msg:delete-message': {
                    'href': '/messages/17',
                    'method': 'DELETE'
                }
            }
        })
        assert doc.root['id'] == 17
        assert doc.root['content'] == 'Hello!'
        assert doc.root.controls['self'].href == 'http://example.org/messages/17'
        assert doc.root.controls['http://example.org/messages/reltypes#delete-message'].href == 'http://example.org/messages/17'
        assert doc.root.controls['http://example.org/messages/reltypes#delete-message'].method == 'DELETE'


class TestInterop(object):
    pass
