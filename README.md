# Voice Box

Voice box is an open source python tool for voice calls and messaging over LAN. Built on top of the TCP/IP protocol.

## Requirements

1. `pyaudio` is the only requirement for capturing your microphone

## How to Run

1. Run `pip install -r requirements.txt` to install all requirements.
2. Run `python your_script.py --port=5679 --bootstrap[<ip of the boostrap node>:<port of the boottrap node>]` or `python -m networking`.
3. Input a username
4. Do the same thing on another machine. Make sure it's connected to the same network.
5. Type the command `call`.
6. Input the machine's IP address and port as displayed in the terminal in the format `ip_address:port`.
7. Accept the connection on the other machine.
8. Have fun.

## Things to Note

1. The program automatically binds to port 4000 and goes to the next port if it's already in use. You can change the default port in the `networking/__main__.py` file.
2. To view the list of possible commands, type in `help` or `h`.
