''' Builder for mason documents. '''

try:
    import bottle
except ImportError:
    pass


class Builder(object):
    def __init__(self, namespaces=None):
        self.namespaces = namespaces or {}

    def build_for_bottle(self, doc):
        accept = bottle.request.get_header('Accept', '')
        prefer = bottle.request.get_header('Prefer', '')
        return self.build(doc, accept=accept, prefer=prefer)

    def build(self, doc, accept='', prefer=''):
        if accept == 'application/json':
            cls = JsonBuilder
        elif 'representation=minimal' in prefer:
            cls = MinimalBuilder
        else:
            cls = FullBuilder
        return cls(self.namespaces, doc).build()


class Object(object):
    def __init__(self, path, data):
        self.data = data
        self.controls = Controls()
        self.controls.add('self', path)


class JsonBuilder(object):
    def __init__(self, namespaces, doc):
        self.doc = doc

    def build(self):
        return self._build_object(self.doc.root)

    def _build(self, item):
        if isinstance(item, list):
            return map(self._build, item)
        if isinstance(item, Object):
            return self._build_object(item)
        return item

    def _build_object(self, obj):
        return {k: self._build(v) for k, v in obj.data.items()}


class FullBuilder(object):
    def __init__(self, namespaces, doc):
        self.namespaces = namespaces
        self.doc = doc

    def build(self):
        out = self._build(self.doc.root)
        if self.namespaces:
            out['@namespaces'] = self._build_namespaces(self.namespaces)
        return out

    def _build(self, item):
        if isinstance(item, list):
            return map(self._build, item)
        if isinstance(item, Object):
            return self._build_object(item)
        return item

    def _build_namespaces(self, namespaces):
        return {k: {'name': v} for k, v in namespaces.items()}

    def _build_object(self, obj):
        res = {k: self._build(v) for k, v in obj.data.items()}
        res['@controls'] = self._build_controls(obj.controls)
        return res

    def _build_controls(self, controls):
        out = {}
        for ctrl in controls.controls:
            name = self._find_curie(ctrl.name)
            out[name] = self._build_control(ctrl)
        return out

    def _find_curie(self, name):
        for k, v in self.namespaces.items():
            if name.startswith(v):
                return name.replace(v, k + ':')
        return name

    def _build_control(self, control):
        params = vars(control).copy()
        params.pop('name')

        out = {'href': params.pop('href')}

        method = params.pop('method')
        if method is not None:
            out['method'] = method

        template = params.pop('template')
        if template is not None:
            out['template'] = template

        for k, v in params.items():
            if v is not None:
                raise NotImplemented(k)

        return out


class MinimalBuilder(object):
    def __init__(self, doc):
        self.doc = doc

    def build(self):
        out = self._build_object(self.doc.root)
        if self.doc.namespaces:
            out['@namespaces'] = self._build_namespaces(self.doc.namespaces)
        return out

    def _build(self, item):
        if isinstance(item, list):
            return map(self._build, item)
        if isinstance(item, Object):
            return self._build_object(item)
        return item

    def _build_namespaces(self, namespaces):
        return {k: {'name': v} for k, v in namespaces.name_uri_dict.items()}

    def _build_object(self, obj):
        res = {k: self._build(v) for k, v in obj.data.items()}
        res['@controls'] = self._build_controls(obj.controls)
        return res

    def _build_controls(self, controls):
        out = {}
        for ctrl in controls.controls:
            name = self._find_curie(ctrl.name)
            out[name] = self._build_control(ctrl)
        return out

    def _find_curie(self, name):
        for k, v in self.namespaces.items():
            if name.startswith(v):
                return k
        return name

    def _build_control(self, control):
        params = vars(control).copy()
        params.pop('name')

        out = {'href': params.pop('href')}

        method = params.pop('method')
        if method is not None:
            out['method'] = method

        template = params.pop('template')
        if template is not None:
            out['template'] = template

        for k, v in params.items():
            if v is not None:
                raise NotImplemented(k)

        return out


class Document(object):
    def __init__(self, root=None):
        self.namespaces = {}
        self.root = root


class Controls(object):
    def __init__(self, controls=None):
        self.controls = controls or []

    def add(self, name, href, **kwargs):
        self.controls.append(Control(name, href, **kwargs))


class Control(object):
    def __init__(self, name, href, is_href_template=None, title=None,
            description=None, method=None, encoding=None, schema=None,
            schema_url=None, template=None, accept=None, output=None,
            files=None, alt=None):
        self.name = name
        self.href = href
        self.is_href_template = is_href_template
        self.title = title
        self.description = description
        self.method = method
        self.encoding = encoding
        self.schema = schema
        self.schema_url = schema_url
        self.template = template
        self.accept = accept
        self.output = output
        self.files = files
        self.alt = alt
