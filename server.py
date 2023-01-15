# simple websockets brocaster
import asyncio
import websockets
import json

clients = []  # to store all connected cleints
players = []
over2People = []
territory = [[0 for i in range(5)] for j in range(5)]


def cal_score(state):
    scoreP1 = 0
    scoreP2 = 0
    for i in range(len(state)):
        for j in range(len(state)):
            if state[i][j] > 0:
                scoreP1 = scoreP1 + 1
            elif state[i][j] < 0:
                scoreP2 = scoreP2 + 1
    return str(scoreP1), str(scoreP2)


# handler for socket message activities
async def handler(websocket, path):
    # print(path) #path is not used currently
    if websocket not in clients:
        clients.append(websocket)  # append new client to the array
    async for message in websocket:
        global players
        global territory
        global over2People
        msg = message.split('#')
        print(msg, 'received from client')  # print to console
        if msg[0] == "play":
            if len(players) >= 2:
                over2People.append(websocket)
                await websocket.send("房間已滿人")
            else:
                players.append(websocket)
                n = len(players)
                n = str(n)
                await broadcast_click(n + "#prepare")
        elif msg[0] == "login":
            n = len(players)
            n = str(n)
            if len(players) >= 2:
                await websocket.send("房間已滿人")
            else:
                await broadcast(n)
        elif msg[0] == "clickSquare":
            left = players[0]
            msg[1] = str(msg[1])
            row = int(msg[1][1])
            column = int(msg[1][0])
            if websocket == left:
                territory[row][column] = territory[row][column] + 1
            elif websocket == players[1]:
                territory[row][column] = territory[row][column] - 1
            r = msg[1][1]
            c = msg[1][0]
            point = str(territory[row][column])
            scoreP1, scoreP2 = cal_score(territory)
            await attack(r + "#" + c + "#" + point + "#" + "clickSquare" + "#" + scoreP1 + "#" + scoreP2)
        elif msg[0] == "stop":
            scoreP1, scoreP2 = cal_score(territory)
            winner = 0
            if scoreP1 < scoreP2:
                winner = 1
            elif scoreP1 == scoreP2:
                winner = 2
            scoreP1 = str(scoreP1)
            scoreP2 = str(scoreP2)
            winner = str(winner)
            await attack(scoreP1 + "#" + scoreP2 + "#" + winner + "#" + "end")
        elif msg[0] == "quit":
            players = []
            territory = [[0 for i in range(5)] for j in range(5)]
            await broadcast_click("0" + "#prepare")

async def broadcast_click(msg):
    m = msg.split("#")
    await broadcast(m[0])
    print(msg, 'show_number')
    for websock in clients:
        try:
            await websock.send(msg)  # send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup")
            clients.remove(websock)

async def broadcast(msg):
    print(msg, 'show_number')
    for websock in clients:
        if websock not in over2People:
            try:
                await websock.send(msg)  # send message to each client
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected. Do cleanup")
                clients.remove(websock)

async def attack(msg):
    print(msg, 'color')
    for websock in players:
        try:
            await websock.send(msg)  # send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup")
            clients.remove(websock)

# starts the service and run forever
loop = asyncio.new_event_loop()  # get an event loop
asyncio.set_event_loop(loop)  # set the event loop to asyncio
loop.run_until_complete(
    websockets.serve(handler, 'localhost', 8787)  # setup the websocket service and handler
)  # hook to localhost:4545
loop.run_forever()  # keep it running
