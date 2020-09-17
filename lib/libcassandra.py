import discord

from .data import Server, User

# Event system
_event_listeners = {}

def get_event_listeners(event):
    if not event in _event_listeners:
        return {}
    return _event_listeners[event]

def add_event_listener(event, who, callback):
    if callback is None or who is None or event is None:
        return False

    if not event in _event_listeners:
        _event_listeners[event] = {}

    get_event_listeners(event)[who] = callback

    return True

def remove_event_listener(event, who):
    if event is None or who is None:
        return False

    del get_event_listeners(event)[who]

    return True

def dispatch(event, args):
    print("#" + event)
    # Convert dictionary to anonymous object
    if type(args) is dict:
        args = type('',(object,),args)()

    # Send to listeners
    for subscriber, callback in get_event_listeners(event).items():
        callback(args)

    # Resturn response
    return args

# Data Storage
_cache_srv = {}
_cache_usr = {}

def load_server(sid):
    # Cache
    if sid in _cache_srv:
        return _cache_srv[sid]

    srv = Server(sid)
    srv.load()

    _cache_srv[sid] = srv

    # Dispatch event
    dispatch("server_load", type('',(object,),{"server": srv})())

    return srv

def save_server(srv):
    # Dispach event
    dispach("server_save", type('',(object,),{"server": srv})())

    srv.save()

    return True

def load_user(srv, uid):
    # Load server if required
    if type(srv) is int:
        srv = get_server(srv)

    # Cache
    cacheid = "%s:%s" % (srv.ID, uid)
    if cacheid in _cache_usr:
        return _cache_usr[cacheid]

    usr = User(srv, uid)
    usr.load()

    _cache_usr[cacheid] = usr

    # Dispatch event
    dispatch("user_load", type('',(object,),{"user": usr})())

    return usr

def save_user(usr):
    # Dispatch event
    dispatch("user_save", type('',(object,),{"user": usr})())

    usr.save()

    return True

def get_server(s):
    if type(s) is int:
        return load_server(s)
    elif type(s) is discord.Guild:
        return load_server(s.id)
    return s

def get_user(u):
    if type(u) is tuple:
        return load_user(u[0], u[1])
    elif type(u) is discord.Member:
        return load_user(u.guild.id, u.id)
    return u
