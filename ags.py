SEPARATOR = ":8&.2/?"
END = "k@72s|/"
KICK = "KICK"
QUESTION = "QUESTION"
REPLY = "REPLY"
ECHO = "ECHO"
PING = "PING"

def encode(txt, msg_type = ECHO):
    return msg_type+SEPARATOR+txt+END

def decode(target):
    message = target.split(END)[0].split(SEPARATOR)
    if len(message) > 1:
        return message[0], message[1]
    if len(message) == 1:
        return message[0], ""
    return "", ""