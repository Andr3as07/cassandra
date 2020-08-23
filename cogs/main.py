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

        if usr.load():
            return usr

        return None

    def save_user(self, srv, usr):
        return False

    def load_server(self, sid):
        print("LOD S %s" % sid)

        srv = Server(sid)

        if srv.load():
            return srv

        return None

    def save_server(self, srv):
        return False

def setup(client):
    client.add_cog(Main(client))
