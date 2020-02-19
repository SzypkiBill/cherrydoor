#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""All websocket routes and functions"""
import functools
from bson import json_util
import json as jsn
from cherrydoor import socket, emit, dt, mongo, current_user, disconnect

__author__ = "opliko"
__license__ = "MIT"
__version__ = "0.3.8"
__status__ = "Prototype"


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)

    return wrapped


@socket.on("stats", namespace="/api")
@authenticated_only
def stats(json={}):
    try:
        time_from = dt.datetime.fromisoformat(json["time_from"].replace("Z", ""))
    except KeyError:
        time_from = dt.datetime.today() - dt.timedelta(days=7)
    try:
        time_to = dt.datetime.fromisoformat(json["time_to"].replace("Z", ""))
    except KeyError:
        time_to = dt.datetime.now()

    results = mongo.logs.find(
        {"timestamp": {"$lt": time_to, "$gte": time_from}}, {"card": 0, "_id": 0}
    )
    json_results = [jsn.dumps(doc, default=json_util.default) for doc in results]
    emit("stats", json_results, namespace="/api")
    return json_results


@socket.on("user", namespace="/api")
@authenticated_only
def user(json={}):
    try:
        username = json["username"]
        user = mongo.users.find_one({"username": username}, {"password": 0, "_id": 0})
        if not user:
            raise KeyError
    except KeyError:
        try:
            card = json["card"]
            user = mongo.users.find_one({"cards": card}, {"password": 0, "_id": 0})
            if not user:
                raise KeyError
        except KeyError:
            return False
    try:
        if json["edit"]:
            mongo.users.update_one(user, json["changes"])
    except KeyError:
        pass
    emit("user", user)
    return user


@socket.on("users", namespace="/api")
@authenticated_only
def users():
    try:
        users = mongo.users.find({}, {"password": 0, "_id": 0})
        json_results = [jsn.dumps(doc, default=json_util.default) for doc in users]
    except:
        return False
    emit("users", json_results)
    return json_results


@socket.on("break_times", namespace="/api")
@authenticated_only
def break_times(json=[]):
    if isinstance(json, list) and len(json) != 0 and isinstance(json[0], list):
        if not any(json[0]):
            mongo.settings.update(
                {"setting": "break_times"},
                {"setting": "break_times", "value": []},
                upsert=True,
            )
            emit("break_times", [])
            return []
        try:
            breaks = [
                [
                    dt.datetime.fromisoformat(item[0].replace("Z", "")),
                    dt.datetime.fromisoformat(item[1].replace("Z", "")),
                ]
                for item in json
            ]
        except IndexError:
            return None
        mongo.settings.update(
            {"setting": "break_times"},
            {"setting": "break_times", "value": breaks},
            upsert=True,
        )
        return_breaks = jsn.dumps(breaks, indent=4, sort_keys=True, default=str)
        emit("break_times", return_breaks)
        return return_breaks
    try:
        breaks = list(mongo.settings.find_one({"setting": "break_times"})["value"])
        breaks = [[item[0].isoformat(), item[1].isoformat()] for item in breaks]
        return_breaks = jsn.dumps(breaks, indent=4, sort_keys=True, default=str)
    except KeyError:
        return None
    emit("break_times", return_breaks)
    return return_breaks
