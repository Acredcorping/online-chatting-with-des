from chat.utils import des_util
import base64


class DES:
    def __init__(self):
        self.decrypt_R = None          # 解密时的右半部分
        self.decrypt_L = None          # 解密时的左半部分
        self.sub_keys = None           # 存储16轮子密钥
        self.encrypt_L = None          # 加密时的左半部分
        self.encrypt_R = None          # 加密时的右半部分
        self.binary_plain_text_blocks = None    # 存储明文分块后的二进制字符串
        self.key = None                # 密钥
        self.plain_text = None         # 明文
        self.plain_binary = None       # 明文二进制比特流
        self.cypher_text = None        # 密文
        self.cypher_binary = None      # 密文二进制比特流
        self.plain_text_binary = None  # 明文二进制字符串
        self.cypher_text_binary = None # 密文二进制字符串
        self.sub_key_binary = None     # 子密钥二进制字符串
        self.ip_table = des_util.IP_TABLE              # 初始置换表
        self.inv_ip_table = des_util.INV_IP_TABLE      # 逆初始置换表
        self.e_table = des_util.E_TABLE                # 扩展置换表
        self.p_table = des_util.P_TABLE                # P置换表
        self.s_box = des_util.S_BOX                    # S盒
        self.pc1_table = des_util.PC1_TABLE            # PC1置换表
        self.pc2_table = des_util.PC2_TABLE            # PC2置换表

    # 将明文分块，每块64位，不足64位的补0
    def handled_plain_text(self):
        if type(self.plain_text) == bytes:
            # 定义临时变量，用于存储处理后的明文
            tmp_plain_text = self.plain_text
        else:
            # 定义临时变量，用于存储处理后的明文
            tmp_plain_text = self.plain_text.encode('utf-8')
        # 计算需要补几个0
        pad_len = 8 - (len(tmp_plain_text) % 8)
        # 补0
        tmp_plain_text += pad_len * b"\x00"
        # 将字符转换成二进制字符串
        binary_plain_text = ''.join([bin(c)[2:].rjust(8, '0') for c in tmp_plain_text])
        # 计算需要分成几块
        num_blocks = len(binary_plain_text) // 64
        # 分块装入列表
        self.binary_plain_text_blocks = [binary_plain_text[i * 64:(i + 1) * 64] for i in range(num_blocks)]

    # 生成16个子密钥(ki, i=1,2,...,16)
    def sub_key_generation(self):
        # 定义临时变量，用于存储处理后的明文
        tmp_key = self.key.encode()
        # 计算需要补几个0
        pad_len = 8 - (len(self.key) % 8)
        # 补0
        tmp_key += pad_len * b"\x00"
        # 将密钥转换成二进制字符串
        binary_key = ''.join([bin(c)[2:].rjust(8, '0') for c in tmp_key])
        # 将密钥进行PC1置换
        pc1_key = self.permutation(binary_key, self.pc1_table)
        # 将置换后的密钥分成两部分
        c0, d0 = self.split_block(pc1_key)
        # 定义16个子密钥
        sub_keys = []
        # 定义左移位数
        shift = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
        # 生成16个子密钥
        for i in range(16):
            c0 = self.left_shift(c0, shift[i])
            d0 = self.left_shift(d0, shift[i])
            sub_keys.append(self.permutation(c0 + d0, self.pc2_table))
        self.sub_keys = sub_keys

    # 加密 - f操作
    def f(self, r, sub_key):
        # 将r进行E扩展
        r = self.permutation(r, self.e_table)
        # 将r与子密钥进行异或
        r = bin(int(r, 2) ^ int(sub_key, 2))[2:].rjust(48, '0')
        # 将r分成8组
        r_blocks = [r[i * 6:(i + 1) * 6] for i in range(8)]
        # 将r分组进行S盒替换
        # 4bit * 8
        s_box_result = []
        for i in range(8):
            # s_i盒的行号为r_i的首尾bit连起来转十进制
            row = int(r_blocks[i][0] + r_blocks[i][-1], 2)
            # s_i盒的列号为r_i的中间4bit连起来转十进制
            col = int(r_blocks[i][1:-1], 2)
            # 将S盒替换后的结果转换成二进制字符串并补全4位
            s_box_result.append(bin(self.s_box[i][row][col])[2:].rjust(4, '0'))
        # 将S盒替换后的结果进行P置换
        s_box_result = self.permutation(''.join(s_box_result), self.p_table)
        return s_box_result

    # 加密 - 加密一次
    def encrypt_one(self, l, r, i):
        # l_i+1 = r_i
        self.encrypt_L = r
        # r_i+1 = l_i ^ f(r_i, k_i)
        self.encrypt_R = bin(int(l, 2) ^ int(self.f(r, self.sub_keys[i]), 2))[2:].rjust(32, '0')

    # 解密 - 解密一次
    def decrypt_one(self, l, r, i):
        # l_i+1 = r_i
        self.decrypt_L = r
        # r_i+1 = l_i ^ f(r_i, k_i)
        self.decrypt_R = bin(int(l, 2) ^ int(self.f(r, self.sub_keys[i]), 2))[2:].rjust(32, '0')

    # 加密 - 加密过程
    def encrypt(self, plain_text, key):
        # 设置明文和密钥
        self.plain_text = plain_text
        self.key = key
        # 处理明文
        self.handled_plain_text()
        # 生成子密钥
        self.sub_key_generation()
        # 定义加密后的二进制字符串
        cypher_binary = ''
        # 对每一块进行加密
        for block in self.binary_plain_text_blocks:
            # 将明文进行IP置换
            block = self.permutation(block, self.ip_table)
            # 将一个block内分为L和R
            tmp_L, tmp_R = self.split_block(block)
            # 加密16轮
            for i in range(16):
                self.encrypt_one(tmp_L,tmp_R, i)
                tmp_L = self.encrypt_L
                tmp_R = self.encrypt_R
            # 合并结果，将结果进行逆ip变换
            cypher_binary += self.permutation(self.encrypt_R + self.encrypt_L, self.inv_ip_table)
            self.cypher_binary = cypher_binary
        # 将二进制字符串转换为base64字符串
        cypher_base64_string = self.bin_to_base64(cypher_binary)
        self.cypher_text = cypher_base64_string

    # 解密
    def decrypt(self, cypher_text, key, base_64=True):
        # 设置密文和密钥
        self.cypher_text = cypher_text
        self.key = key
        if base_64:
            # 将base64字符串转换为二进制字符串
            cypher_binary = self.base64_to_bin(cypher_text)
        else:
            cypher_binary = cypher_text
        # 将二进制字符串分成64位一组
        cypher_binary_blocks = [cypher_binary[i * 64:(i + 1) * 64] for i in range(len(cypher_binary) // 64)]
        # 生成子密钥
        self.sub_key_generation()
        # 16轮解密
        plain_binary = ''
        for block in cypher_binary_blocks:
            # 将密文进行IP置换
            block = self.permutation(block, self.ip_table)
            # 将一个block内分为L和R
            tmp_L, tmp_R = self.split_block(block)
            # 解密16轮
            for i in reversed(range(16)):
                self.decrypt_one(tmp_L, tmp_R, i)
                tmp_L = self.decrypt_L
                tmp_R = self.decrypt_R
            # 合并结果，将结果进行逆ip变换
            plain_binary += self.permutation(self.decrypt_R + self.decrypt_L, self.inv_ip_table)
        # 将二进制字符串转换成字节流
        plain_byte = int(plain_binary, 2).to_bytes((len(plain_binary) + 7) // 8, 'big')
        self.plain_binary = plain_byte
        try:
            # 将字节流转换成utf-8编码的字符串
            plain_string = plain_byte.decode('utf-8').strip('\x00')
            self.plain_text = plain_string
        except:
            self.plain_text = self.bin_to_base64(plain_byte)

    # 左移shift_num位, 移什么补什么
    @staticmethod
    def left_shift(origin_str, shift_num):
        return origin_str[shift_num:] + origin_str[:shift_num]

    # IP变换
    @staticmethod
    def permutation(text, grid):
        return ''.join([text[i - 1] for i in grid])

    # 将字符串对半分
    @staticmethod
    def split_block(origin_str):
        return origin_str[:len(origin_str) // 2], origin_str[len(origin_str) // 2:]

    @staticmethod
    def bin_to_base64(binary_string):
        if type(binary_string) == str:
            # 将二进制字符串转换成字节流
            string_byte = int(binary_string, 2).to_bytes((len(binary_string) + 7) // 8, 'big')
            # 将字节流转换成base64字符串
            string_base64 = base64.b64encode(string_byte)
            # 将base64字符串转换成字符串
            return string_base64.decode('utf-8')
        else:
            # 将字节流转换成base64字符串
            string_base64 = base64.b64encode(binary_string)
            # 将base64字符串转换成字符串
            return string_base64.decode('utf-8')

    @staticmethod
    def base64_to_bin(base64_string):
        # Base64解码
        binary_bytes = base64.b64decode(base64_string)
        # 转换为二进制字符串
        return bin(int.from_bytes(binary_bytes, 'big'))[2:].zfill(len(binary_bytes) * 8)