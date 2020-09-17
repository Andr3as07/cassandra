from .data import Server, User

client = None

_cache_srv = {}
_cache_usr = {}

def load_server(sid):
    # Cache
    if sid in _cache_srv:
        return _cache_srv[sid]

    print("LODS %s" % sid)
    srv = Server(sid)
    srv.load()

    _cache_srv[sid] = srv

    return srv

def save_server(srv):
    print("SAVS %s" % srv.ID)

    srv.save()

    return True

def load_user(srv, uid):
    # Load server if required
    if type(srv) is int:
        srv = load_server(srv)

    # Cache
    cacheid = "%s:%s" % (srv.ID, uid)
    if cacheid in _cache_usr:
        return _cache_usr[cacheid]

    print("LODU %s %s" % (srv.ID, uid))
    usr = User(srv, uid)
    usr.load()

    _cache_usr[cacheid] = usr

    return usr

def save_user(usr):
    print("SAVU %s %s" % (usr.server.ID, usr.ID))
    usr.save()

    return True

def get_server(s):
    if type(s) is int:
        return load_server(s)
    return s

def get_user(u):
    if type(u) is tuple:
        return load_user(u[0], u[1])
    return u
