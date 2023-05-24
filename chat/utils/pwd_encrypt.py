import bcrypt


def hash_password(password):
    # 生成随机的 salt
    salt = bcrypt.gensalt()
    # 使用 salt 和密码生成哈希值
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # 返回加密后的密码
    return hashed_password.decode('utf-8')


def verify_password(password, hashed_password):
    # 验证密码是否匹配
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
