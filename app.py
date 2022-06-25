#!/usr/bin/env python

# author: thomas

import asyncio
import json
import os
import secrets
import signal

import websockets

from connect4 import PLAYER1, PLAYER2, Connect4

JOIN = {}
WATCH = {}


async def error(websocket, message):
    """
    Send an error message.
    """
    event = {
        "type": "error",
        "message": message,
    }
    await websocket.send(json.dumps(event))


async def replay(websocket, game):
    """
    Send previous moves.

    """
    # Make a copy to avoid an exception if game.moves changes while iteration
    # is in progress. If a move is played while replay is running, moves will
    # be sent out of order but each move will be sent once and eventually the
    # UI will be consistent.
    for moveI, (player, column, row) in enumerate(game.moves.copy()):
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
            "moves": moveI+1,
        }
        await websocket.send(json.dumps(event))


async def play(websocket, game, player, websocketSet):
    """
    Receive and process moves from a player.
    """
    async for message in websocket:
        # Parse a "play" event from the UI.
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            await error(websocket, str(exc))
            continue

        # Send a "play" event to update the UI.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
            "moves": len(game.moves),
        }
        websockets.broadcast(websocketSet, json.dumps(event))

        # If move is winning, send a "win" event.
        if game.winner is not None:
            event = {
                "type": "win",
                "player": game.winner,
            }
            websockets.broadcast(websocketSet, json.dumps(event))


async def start(websocket, join=None):
    """
    Handle a connection from the first player: start a new game.
    """
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access tokens.
    game = Connect4()
    websocketSet = {websocket}

    if join:
        join_key = join
    else:
        join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, websocketSet

    watch_key = secrets.token_urlsafe(12)
    WATCH[watch_key] = game, websocketSet

    game.saveLinkIDs(game, websocketSet, join_key, watch_key)

    try:
        # Send the secret access tokens to the browser of the first player,
        # where they'll be used for building "join" and "watch" links.
        event = {
            "type": "init",
            "player": "player1",
            "join": join_key,
            "watch": watch_key,
            "start": game.start,
        }
        await websocket.send(json.dumps(event))
        # Receive and process moves from the first player.
        await play(websocket, game, PLAYER1, websocketSet)
    finally:
        del JOIN[join_key]
        del WATCH[watch_key]


async def join(websocket, join_key):
    """
    Handle a connection from the second player: join an existing game.

    """
    # Find the Connect Four game.
    try:
        game, websocketSet = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    websocketSet.add(websocket)
    try:
        # Send the init requests to the browser
        event = {
            "type": "init",
            "player": "player2",
            "join": game.join,
            "watch": game.watch,
            "start": game.start,
        }
        await websocket.send(json.dumps(event))
        # Send the first move, in case the first player already played it.
        await replay(websocket, game)
        # Receive and process moves from the second player.
        await play(websocket, game, PLAYER2, websocketSet)
    finally:
        websocketSet.remove(websocket)


async def watch(websocket, watch_key):
    """
    Handle a connection from a spectator: watch an existing game.

    """
    # Find the Connect Four game.
    try:
        game, websocketSet = WATCH[watch_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    websocketSet.add(websocket)
    try:
        # Send the init requests to the browser
        event = {
            "type": "init",
            "player": "spectator",
            "watch": game.watch,
            "start": game.start,
        }
        await websocket.send(json.dumps(event))
        # Send previous moves, in case the game already started.
        await replay(websocket, game)
        # Keep the connection open, but don't receive any messages.
        await websocket.wait_closed()
    finally:
        websocketSet.remove(websocket)


async def handler(websocket, path):
    """
    Handle a connection and dispatch it according to who is connecting.

    """
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])
    elif "watch" in event:
        # Spectator watches an existing game.
        await watch(websocket, event["watch"])
    else:
        # First player starts a new game.
        if "joinID" in event:
            await start(websocket, event["joinID"])
        else:
            await start(websocket)


async def main():
    # Set the stop condition when receiving SIGTERM.
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
