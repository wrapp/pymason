''' Parser for mason documents. '''

from urlparse import urljoin


def parse(source_url, data):
    return Parser(source_url, data).parse()


class Parser(object):
    def __init__(self, source_url, data):
        self.source_url = source_url
        self.data = data
        self.namespaces = {k: v['name']
                for k, v in self.data.pop('@namespaces', {}).items()}
        self.meta = self.data.pop('@meta', {})

    def parse(self):
        root = self._parse_object(self.data)
        return Document(root, self.meta, self.namespaces)

    def _parse(self, data):
        if isinstance(data, dict):
            return self._parse_object(data)
        if isinstance(data, list):
            return map(self._parse, data)
        return data

    def _parse_object(self, data):
        controls_ = data.pop('@controls', {})
        controls = {self._expand_curie(k): self._parse_control(v) for k, v in controls_.items()}
        data = {k: self._parse(v) for k, v in data.items()}
        return Object(data, controls)

    def _parse_control(self, data):
        href = urljoin(self.source_url, data.pop('href'))
        return Control(href, data)

    def _expand_curie(self, name):
        if ':' not in name:
            return name
        namespace, reference = name.split(':')
        if namespace in self.namespaces:
            return self.namespaces[namespace] + reference
        return name


class Document(object):
    def __init__(self, root, meta, namespaces):
        self.meta = meta
        self.namespaces = namespaces
        self.root = root


class Object(dict):
    def __init__(self, data, controls):
        super(Object, self).__init__(data)
        self.controls = controls

    def __repr__(self):
        return 'Object ' + super(Object, self).__repr__()


class Control(object):
    def __init__(self, href, obj):
        self.href = href
        self.is_href_template = obj.get('isHrefTemplate', False)
        self.title = obj.get('title')
        self.description = obj.get('description')
        self.method = obj.get('method', 'GET')
        self.encoding = obj.get('encoding', 'none')
        self.schema = obj.get('schema')
        self.schema_url = obj.get('schema_url')
        self.template = obj.get('template')
        self.accept = obj.get('accept', [])
        self.output = obj.get('output', [])
        self.files = obj.get('files', [])
        self.alt = obj.get('alt', [])

    def __repr__(self):
        return 'Control ' + repr({'href': self.href, 'method': self.method})
