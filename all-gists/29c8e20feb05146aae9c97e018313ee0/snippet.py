"""
Copyright 2017 Google Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import websockets
from s2clientprotocol import sc2api_pb2 as sc_pb

def makeGameRequest():
    req = sc_pb.Request()
    req.create_game.battlenet_map_name = "Ohana LE"
    req.create_game.disable_fog = True
    
    me = req.create_game.player_setup.add()
    me.type = sc_pb.Participant
    me.race = sc_pb.Protoss

    opponent = req.create_game.player_setup.add()
    opponent.type = sc_pb.Participant
    opponent.race = sc_pb.Protoss

    print(req)
    
    return req

def makeJoinGameRequest():
    req = sc_pb.Request()
    req.join_game.race = sc_pb.Protoss
    req.join_game.options.raw = True
    
    req.join_game.shared_port = 5002
    req.join_game.server_ports.game_port = 5003
    req.join_game.server_ports.base_port = 5004
    
    p1 = req.join_game.client_ports.add()
    p1.game_port = 5005
    p1.base_port = 5006

    p2 = req.join_game.client_ports.add()
    p2.game_port = 5007
    p2.base_port = 5008

    print(req)
    
    return req

def makeStepRequest():
    req = sc_pb.Request()
    req.step.count = 8
    
    print(req)
    
    return req

def makeObservationRequest():
    req = sc_pb.Request()
    req.observation.SetInParent()
    
    print(req)
    
    return req

def makeLeaveRequest():
    req = sc_pb.Request()
    req.leave_game.SetInParent()
    
    print(req)
    
    return req

def makeDataRequest():
    req = sc_pb.Request()
    req.data.SetInParent()
    
    print(req)
    
    return req

async def runHost():
    async with websockets.connect('ws://127.0.0.1:5000/sc2api') as websocket:
        await websocket.send(makeGameRequest().SerializeToString())
        
        response = sc_pb.Response()
        response_bytes = await websocket.recv()
        response.ParseFromString(response_bytes)
        print("< {}".format(response))
        
        await websocket.send(makeJoinGameRequest().SerializeToString())
        
        response = sc_pb.Response()
        response_bytes = await websocket.recv()
        response.ParseFromString(response_bytes)
        print("< {}".format(response))
        
        still_going = True
        while still_going:
            await websocket.send(makeObservationRequest().SerializeToString())
        
            response = sc_pb.Response()
            response_bytes = await websocket.recv()
            response.ParseFromString(response_bytes)
            print("< {}".format(response))
            if len(response.observation.player_result) > 0:
                still_going = False
            
            await websocket.send(makeStepRequest().SerializeToString())
        
            response = sc_pb.Response()
            response_bytes = await websocket.recv()
            response.ParseFromString(response_bytes)
            print("< {}".format(response))
        
        await websocket.send(makeLeaveRequest().SerializeToString())
        
        response = sc_pb.Response()
        response_bytes = await websocket.recv()
        response.ParseFromString(response_bytes)
        print("< {}".format(response))

async def runClient():
    async with websockets.connect('ws://127.0.0.1:5001/sc2api') as websocket:        
        await websocket.send(makeJoinGameRequest().SerializeToString())
        
        response = sc_pb.Response()
        response_bytes = await websocket.recv()
        response.ParseFromString(response_bytes)
        print("< {}".format(response))
        
        still_going = True
        while still_going:
            await websocket.send(makeObservationRequest().SerializeToString())
        
            response = sc_pb.Response()
            response_bytes = await websocket.recv()
            response.ParseFromString(response_bytes)
            print("< {}".format(response))
            if len(response.observation.player_result) > 0:
                still_going = False
            
            await websocket.send(makeStepRequest().SerializeToString())
        
            response = sc_pb.Response()
            response_bytes = await websocket.recv()
            response.ParseFromString(response_bytes)
            print("< {}".format(response))
        
        await websocket.send(makeLeaveRequest().SerializeToString())
        
        response = sc_pb.Response()
        response_bytes = await websocket.recv()
        response.ParseFromString(response_bytes)
        print("< {}".format(response))

asyncio.get_event_loop().run_until_complete(asyncio.gather(
    runHost(),
    runClient()
))
