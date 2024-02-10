import logging
import asyncio
from kademlia.network import Server
from voicebox.node import Node, MicrophoneStreamerThread
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)-8s  %(message)s',
    datefmt='(%H:%M:%S)'
)

server = Server()

async def run(port, bootstrap_node,username=None,ip=None):
    """
        Connects to a peer's DHT server.

        This function basically adds this machine to a DHT network

        The first node connecting to the network should not have a bootstrap_ip or bootstrap_port

        The subsequent nodes connecting to the network should have the first node's ip and port as bootstrap_ip and bootstrap_port
    """
    
    event = asyncio.Event()
    await server.listen(port)
    if bootstrap_node:
        try:
            bootstrap_ip, bootstrap_port = bootstrap_node.split(':')
            await server.bootstrap([(bootstrap_ip, int(bootstrap_port))])
            if username == "INIT":
                await event.wait()
            await event.wait()
            #return task,server
        except Exception as e:  # Broader exception handling for debugging
            logging.error(f"Error during bootstrap: {e}")
            pass
    else:
        logging.info("No bootstrap information provided, starting as the first node in the network.")
        await event.wait()
    

def finished(found):
    # The DHT network is ready
    print("DHT network is ready")

async def setusername(server:Server,username, ip, port):
    """
        Set's a username on the DHT
    """
    result = await server.get(username)
    if result is not None:
        return False
    await server.set(username, f"{ip}:{port}")
    return True


async def getusername(server:Server,username):
    """
        Get's connection info linked to a username on DHT
    """
    result = await server.get(username)
    if result is None:
        return ""
    return result


def parse_args():

    """
        Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Voicebox')

    parser.add_argument(
        '--port',
        required=True,
        type=int,
        help='Input port number'
    )

    parser.add_argument(
        '--bootstrap',
        type=str,
        required=False,
        help='Bootstrap like this <bootstrap_ip>:<bootstrap_port>'
    )

    args = parser.parse_args()

    return args


def initiate_call(node: Node):

    """
        Flow to initiate a connection with someone else
    """

    username = input("Input the username of the client to call: ")

    node.connect_to_machine_with_username(username)


async def main():
    """
        Main function that puts everything all together
    """

    args = parse_args()
    # create a node on the network
    success= False
    while not success:
        try:
            username = input("Username: ")
            node ={"ip":"127.0.0.1","port":args.port}# Node(username,port=args.port)
            asyncio.create_task(await run(args.port, args.bootstrap, username, "127.0.0.1"))
            success = await setusername(server,username)
            logging.error("Failed to start the server. Please try again.")
        except ValueError as exc:
            logging.error(f"Error with username: {str(exc)}")
     # Create a background task for the server
    if server:
        server_task = asyncio.create_task(server.start())
        # Welcome message
        print(
            f"Welcome {username}! Others can call you at:{args.port}"
        )

        # Initiate microphone
        MicrophoneStreamerThread.initiate_microphone_stream()

        # Apps menu
        try:
            while True:

                opt = input("> ").lower().replace(' ', '_')

                if opt in ('new_call', 'call', 'new_chat'):

                    initiate_call(node)

                elif opt in ('end_call',):

                    print(node.connection_pool, 'opt', opt)

                    address = input("Input the ip of client to end: ")

                    node.end_call(address)

                elif opt in ('toggle_mute', 'mute'):
                    MicrophoneStreamerThread.MUTED = not MicrophoneStreamerThread.MUTED
                    node.toggle_mute()

                    print("Muted State: ", MicrophoneStreamerThread.MUTED)
                    print("Node Muted State: ", node.muted)

                elif opt in ('send', 'send_msg'):
                    msg = input("Msg: ")
                    list(node.connection_pool.values())[0].send_message(msg, 1)

                elif opt in ('help', 'h'):

                    print("Type 'call' to call, 'mute' to toggle microphone, 'send' to message")
                    print("Type 'view' or 'view_machines' to view connected machines")
                
                elif opt in ('search', 'ss'):
                    name = await getusername(server,input("Username: "))
                    print(f"The name is {name}")
        except KeyboardInterrupt:
            server_task.cancel()
            await server_task
            pass
                
