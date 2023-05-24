from chat.utils.des import DES


def msg_encrypt(msg, key):
    des = DES()
    des.encrypt(msg, key)
    return des.cypher_text


def msg_decrypt(cipher, key):
    des = DES()
    des.decrypt(cipher, key)
    return des.plain_text
