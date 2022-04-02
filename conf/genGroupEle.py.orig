from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import prime192v1,secp256k1,sect283k1,sect571k1, secp160k1 


#192 bit group: g, h
decoded_g192 =  b'\xab\xd0}\x86\xe1\x92,\xdd Ceael\x1a\xc3\xb9\xf5a\xe9K\xcd7\xa4'
decoded_h192 =  b'\x00\xa3\x0brz\xea\xb0\xba\x005\t\xf9\xe9\xd2\x84\x0b\x18\x02\x18\xc2\xd7E\x13D'


group160 = ECGroup(secp160k1)

group192 = ECGroup(prime192v1)
group256 = ECGroup(secp256k1)
group283 = ECGroup(sect283k1)
group571 = ECGroup(sect571k1)


g160 = group160.random(G)
h160 = group160.random(G)

g256 = group256.random(G)
h256 = group256.random(G)

#Cofactor is 4 
#TODO: Just doing 8 change to 4 
g283 = (group283.random(G)) ** (group283.init(ZR, int(4)))
h283 = (group283.random(G)) ** (group283.init(ZR, int(4)))

g571 = (group571.random(G)) ** (group571.init(ZR, int(4)))
h571 = (group571.random(G)) ** (group571.init(ZR, int(4)))


decoded_g160 = group160.decode(g160)
decoded_h160 = group160.decode(h160)

decoded_g256 = group256.decode(g256)
decoded_h256 = group256.decode(h256)

decoded_g283 = group283.decode(g283)
decoded_h283 = group283.decode(h283)

decoded_g571 = group571.decode(g571)
decoded_h571 = group571.decode(h571)

print("decoded_g160:\n", decoded_g160)
print("decoded_h160:\n", decoded_h160)

print("decoded_g256:\n", decoded_g256)
print("decoded_h256:\n", decoded_h256)

print("decoded_g283:\n", decoded_g283)
print("decoded_h283:\n", decoded_h283)

print("decoded_g571:\n", decoded_g571)
print("decoded_h571:\n", decoded_h571)



print("g160:", g160)
g = group160.encode(decoded_g160)
print("g160-enc-dec", g)

print("\n\n")
print("g283:", g283)
g = group283.encode(decoded_g283)
print("g/g:", g/g)
print("decoded encoded g283:", g)
one = group283.init(ZR, int(1))
zero = group283.init(ZR, int(0))

print("g**1:", g** one)
print("g**0:", g**zero)

print("g571:", g571)
g = group571.encode(decoded_g571)
print("g/g:", g/g)
print("decoded encoded g571:", g)
one = group571.init(ZR, int(1))
zero = group571.init(ZR, int(0))

print("g**1:", g** one)
print("g**0:", g**zero)
print("(g**0)*g:", (g**zero)*g)
   
for i in range(20):
    #g1 = group283.random(G)

    #g = g1 ** (group283.init(ZR, int(4)))
    #    print("g:", g)
    #b = group571.init(ZR, int(4))
    #g = group283.random(G)
    #c = (int(a)+ int(b)) % (group571.order())
    #c = group571.init(ZR, int(c))

    a1 = group283.random(ZR)
    b1 = group283.random(ZR)
    c1 = group283.random(ZR)

    a = group571.random(ZR)
    b = group571.random(ZR)
    c = group571.random(ZR)

    g = g571

    d = a + b + c
    D = g ** d


    A = g ** a
    B = g ** b
    C = g ** c
    D1 = (A * B) * C
    
    '''
    print("g:", g)
    print("a:", a)
    print("b:", b)
    print("c:", c)
    print("d:", d)
    print("D:", D)
    print("D1:", D1)
    '''
    if D == D1:
        print("Equal")
    else:
        print("Not Equal")


    #    print("order:", group571.order())
print("\n\n")




