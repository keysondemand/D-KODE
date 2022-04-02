from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import prime192v1, secp256k1, sect283k1,sect571k1, secp160k1

group160 = ECGroup(secp160k1)
group192 = ECGroup(prime192v1)
group256 = ECGroup(secp256k1)
group283 = ECGroup(sect283k1)
group571 = ECGroup(sect571k1)

decoded_g160 =  b'\x00L}\xf8_\xf8\xf9\x14\x86\xa2\xfe_\x93SA\xa6\xab'

decoded_h160 =  b'\x00N\xcc\xd9\x1c\x83\xd5\x843x\xc1,\xabs\xc1,\xbc'

decoded_g192 =  b'\xab\xd0}\x86\xe1\x92,\xdd Ceael\x1a\xc3\xb9\xf5a\xe9K\xcd7\xa4'

decoded_h192 =  b'\x00\xa3\x0brz\xea\xb0\xba\x005\t\xf9\xe9\xd2\x84\x0b\x18\x02\x18\xc2\xd7E\x13D'

decoded_g256 =  b'\xba\x98\x0e\x99\xe1fF\xa5\x08\xc4\x1f%\xae\rz\x85\x83\x14\xc9(\x9e,\x18[,\xc9\x9f\xae'

decoded_h256 =  b'\xb6?[\xe9\xa4&\x02\x84\xf2^\x9e\xe8<\xd52\x11\x8fg\x16.\xa2:o\xd3\xa7\x9e\x14e'

decoded_g283 = b'\x03\xea\xc1\x12\xfd\x03U\xcf\xe7\xdd\xd1\xbe\xb9"\xd0\xeec\xff\xb4~u;\xbb(\xaa?\xb8\xfb\x16\x98|\x8c'

decoded_h283 = b'\x00\xf5+\xe2H*\x13\xa1\xbbW\x91\xd7P\xb4\xf5\xfa\x81\xfb\x12W\x1f\xa1\xaeP8\xb1\x0fE\xc4\xa7F\n'

decoded_g571 =  b'\x00F;V\xc9\x86\xfd-I\xe2\xc9z\xa1\x0c)\x8f\x1c94}\xbc\xd8g\xcc\xda\x13\xac1\xb2\x870?\xa2\xa3\xb2r\x14\x8b\xc3\xbb\x99y$x5V\xee\xf4\xa0\xaa\x87d\xce\xae\xd1\xf3 \xce8\xf2*\x1e\xf9\xc4o\x0f\xf8\xa2'

decoded_h571 = b'\x07g\x93\x0c\xde\xb3\xb8\x1a\xcf\xa8+\n\xf9W&m\xd2q\x97\x17\xd6\xa1W\xa0\xe6\xae\x1a_Z\x02_\xcc\x9f\x97\xc1\x81\x01\x96\\<E\x05f\xe3\xd3S.\x04P\xd6\xad}\x82\xc00\x1b\xc2\xbb\xb5*\xa4~\x91c\x80+\xbex'


#Assign to 'group' the default group of choice 


<<<<<<< HEAD
bits = 283 
#bits = 192
#bits = 256
=======
bits = 283
>>>>>>> 4cd233e09c1d83d2e7cde1fa1f9f88104100d60a

if bits == 160:
    group = group160
    decoded_g = decoded_g160
    decoded_h = decoded_h160
    g = group.encode(decoded_g160) 
    h = group.encode(decoded_h160) 


if bits == 192:    
    group = group192
    decoded_g = decoded_g192
    decoded_h = decoded_h192
    g= group.encode(decoded_g192, True) 
    h= group.encode(decoded_h192, True)

elif bits == 256:
    group = group256
    decoded_g = decoded_g256
    decoded_h = decoded_h256
    g = group.encode(decoded_g256) 
    h = group.encode(decoded_h256) 

elif bits == 283:
    group     = group283
    decoded_g = decoded_g283
    decoded_h = decoded_h283
    g = group.encode(decoded_g283) ** group.init(ZR, int(4))
    h = group.encode(decoded_h283) ** group.init(ZR, int(4))

elif bits == 571:
    group     = group571
    decoded_g = decoded_g571
    decoded_h = decoded_h571
    g = group.encode(decoded_g571) ** group.init(ZR, int(4))
    h = group.encode(decoded_h571) ** group.init(ZR, int(4))

g_rand = group.random(G)
zero   = group.init(ZR, int(0))
unity  = g_rand ** zero


g256 = group256.encode(decoded_g256)
h256 = group256.encode(decoded_h256)

g283 = group283.encode(decoded_g283) ** group283.init(ZR, int(4))
h283 = group283.encode(decoded_h283) ** group283.init(ZR, int(4))

g571 = group571.encode(decoded_g571) ** group571.init(ZR, int(4))
h571 = group571.encode(decoded_h571) ** group571.init(ZR, int(4))
