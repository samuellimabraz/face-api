import asyncio
import websockets
import json
import os

async def test_websocket():
    api_key = "wqKN0jaGDh2JOjpny-eEzDZA9ZSW0JuFq81y2NyyFP8"
    org = "test_org"
    user= "webscoket"
    api_key_name = "webscoket"
    uri = f"ws://localhost:8000/ws/recognize?token={api_key}&organization={org}&user={user}&api_key_name={api_key_name}"
    
    async with websockets.connect(uri) as websocket:
        # Enviar dados de teste
        await websocket.send(json.dumps({
            "image": "/home/samuel/Codes/unifei/ecot01a/project/assets/images/test_image.jpg",
            "threshold": 0.5,
            "organization": org
        }))
        
        # Receber resposta
        response = await websocket.recv()
        print("Received data:", response)
        
async def test_websocket_multiple_messages():
    api_key = "wqKN0jaGDh2JOjpny-eEzDZA9ZSW0JuFq81y2NyyFP8"
    org = "test_org"
    user= "webscoket"
    api_key_name = "webscoket"
    uri = f"ws://localhost:8000/ws/recognize?token={api_key}&organization={org}&user={user}&api_key_name={api_key_name}"
    
    root_dir = "/home/samuel/Codes/unifei/ecot01a/project/assets/images"
    images = [os.path.join(root_dir, path) for path in os.listdir(root_dir) if path.endswith(".jpg")]
        
    async with websockets.connect(uri) as websocket:
        for image in images:
            # Enviar dados de teste
            await websocket.send(json.dumps({
                "image": image,
                "threshold": 0.5,
                "organization": org
            }))
            
            # Receber resposta
            response = await websocket.recv()
            print(f"Received data for {image}:", response)

asyncio.get_event_loop().run_until_complete(test_websocket_multiple_messages())

# asyncio.get_event_loop().run_until_complete(test_websocket())