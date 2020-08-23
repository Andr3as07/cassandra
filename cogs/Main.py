import discord
import os
import json
from discord.ext import commands
from lib.data import User, Server

class Main(commands.Cog):
    def __init__(self, client):
        self.client = client

    def load_user(self, srv, uid):
        if type(srv) is int:
            srv = self.load_server(srv)

        print("LOD U %s %s" % (srv.ID, uid))

        usr = User(srv, uid)
        usr.load()
        return usr

    def save_user(self, usr):
        print("SAV U %s %s" % (usr.server.ID, usr.ID))

        usr.save()

        return True

    def load_server(self, sid):
        print("LOD S %s" % sid)

        srv = Server(sid)
        srv.load()

        return srv

    def save_server(self, srv):
        return False

def setup(client):
    client.add_cog(Main(client))
