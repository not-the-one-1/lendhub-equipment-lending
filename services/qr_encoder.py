"""ISO/IEC 18004 byte-mode encoder, version 2-L, mask 0 (32-byte limit).

This deliberately small encoder supports the ASCII LendHub equipment URI only.
No image or QR libraries are needed to generate a printable PNG.
"""
import struct
import zlib
from pathlib import Path

def matrix(payload):
    raw=payload.encode('ascii')
    if len(raw)>32: raise ValueError('QR payload must be at most 32 ASCII bytes.')
    bits=[0,1,0,0]+[(len(raw)>>i)&1 for i in range(7,-1,-1)]
    for b in raw: bits += [(b>>i)&1 for i in range(7,-1,-1)]
    bits += [0]*min(4,272-len(bits)); bits += [0]*((-len(bits))%8)
    data=[sum(bits[i+j]<<(7-j) for j in range(8)) for i in range(0,len(bits),8)]
    padding=0
    while len(data)<34:
        data.append(0xEC if padding%2==0 else 0x11); padding+=1
    def mul(a,b):
        out=0
        for _ in range(8):
            if b&1: out^=a
            b>>=1; a<<=1
            if a&256: a^=0x11D
        return out
    generator=[1]; root=1
    for _ in range(10):
        out=[0]*(len(generator)+1)
        for i,c in enumerate(generator): out[i]^=c; out[i+1]^=mul(c,root)
        generator=out; root=mul(root,2)
    rem=data+[0]*10
    for i in range(len(data)):
        factor=rem[i]
        for j,c in enumerate(generator): rem[i+j]^=mul(c,factor)
    stream=[]
    for b in data+rem[-10:]: stream += [(b>>i)&1 for i in range(7,-1,-1)]
    n=25; grid=[[None]*n for _ in range(n)]
    def setxy(x,y,v):
        if 0<=x<n and 0<=y<n: grid[y][x]=int(v)
    for ox,oy in ((0,0),(18,0),(0,18)):
        for y in range(-1,8):
            for x in range(-1,8):
                black=0<=x<=6 and 0<=y<=6 and (x in (0,6) or y in (0,6) or (2<=x<=4 and 2<=y<=4))
                setxy(ox+x,oy+y,black)
    for i in range(8,n-8): setxy(i,6,i%2==0); setxy(6,i,i%2==0)
    for y in range(-2,3):
        for x in range(-2,3): setxy(18+x,18+y,max(abs(x),abs(y))!=1)
    fmt=0x77C4  # L, mask 0, BCH format string including the fixed XOR mask.
    for i in range(15):
        bit=(fmt>>i)&1
        if i<6: setxy(8,i,bit)
        elif i<8: setxy(8,i+1,bit)
        else: setxy(8,n-15+i,bit)
        if i<8: setxy(n-i-1,8,bit)
        elif i<9: setxy(15-i,8,bit)
        else: setxy(15-i-1,8,bit)
    setxy(8,n-8,1)
    index=0; upward=True; right=n-1
    while right>=1:
        if right==6: right-=1
        for row in range(n):
            y=n-1-row if upward else row
            for x in (right,right-1):
                if grid[y][x] is None:
                    bit=stream[index] if index<len(stream) else 0
                    grid[y][x]=bit^int((x+y)%2==0); index+=1
        upward=not upward; right-=2
    return grid

def write_png(path,payload,scale=10):
    cells=matrix(payload); size=33*scale
    raw=bytearray()
    for y in range(33):
        row=bytearray()
        for x in range(33):
            black=4<=x<29 and 4<=y<29 and cells[y-4][x-4]
            row.extend(bytes([0 if black else 255])*scale)
        for _ in range(scale): raw.extend(b'\x00'+row)
    def chunk(name,data):
        return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw)))+chunk(b'IEND',b'')
    Path(path).write_bytes(png)
    return str(path)
