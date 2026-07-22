import socket
import struct
import time
def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc
def parse_frame(data):
    if len(data) < 7:
        return None, None
    if data[0] != 0xAA or data[1] != 0x55:
        return None, None
    cmd = data[2]
    length = data[3]
    if len(data) < 4 + length + 2:
        return None, None
    recv_crc = struct.unpack('<H', data[4+length:4+length+2])[0]
    calc_crc = crc16(data[2:4+length])
    if recv_crc != calc_crc:
        return None, None
    return cmd, data[4:4+length]
def recv_frame(sock, timeout=2):
    """循环接收直到收到有效帧或超时"""
    data = b''
    start_time = time.time()
    while time.time() - start_time < timeout:
        chunk = sock.recv(256)
        if not chunk:
            break
        data += chunk
        # 查找 0xAA 开头的帧
        pos = data.find(b'\xAA')
        if pos != -1:
            # 从 0xAA 开始截取
            data = data[pos:]
            # 尝试解析
            cmd, payload = parse_frame(data)
            if cmd is not None:
                return cmd, payload
            # 如果数据不够，继续读取
        # 如果数据过长且没有有效帧，丢弃一部分
        if len(data) > 256:
            data = data[-256:]
    return None, None
s = socket.socket()
s.connect(('localhost', 4444))
s.settimeout(2)
# 发送查询指令
s.send(b'\xAA\x55\x03\x00\x00\x00')
time.sleep(0.1)  # 等待 telnet 协商完成
# 接收帧
cmd, payload = recv_frame(s, timeout=3)
if cmd == 0x81:
    joints = struct.unpack('<6f', payload)
    print('关节角度:', [round(j, 3) for j in joints])
else:
    print('未收到有效响应')
s.close()
