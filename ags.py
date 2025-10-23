SEPARATOR = ":8&.2/?"
KICK = "KICK"
QUESTION = "QUESTION"
REPLY = "REPLY"
ECHO = "ECHO"
PING = "PING"

def msg(txt, msg_type = ECHO):
    return msg_type+SEPARATOR+txt

def signal(msg_type = PING):
    return msg_type

def decode(target):
    message = target.split(SEPARATOR)
    if len(message) > 1:
        return message[0], message[1]
    if len(message) == 1:
        return message[0], ""
    return "", ""