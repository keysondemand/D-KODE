import time 


from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import prime192v1,secp256k1,sect283k1,sect571k1 


#192 bit group: g, h
decoded_g192 =  b'\xab\xd0}\x86\xe1\x92,\xdd Ceael\x1a\xc3\xb9\xf5a\xe9K\xcd7\xa4'
decoded_h192 =  b'\x00\xa3\x0brz\xea\xb0\xba\x005\t\xf9\xe9\xd2\x84\x0b\x18\x02\x18\xc2\xd7E\x13D'

group192 = ECGroup(prime192v1)
group256 = ECGroup(secp256k1)
group283 = ECGroup(sect283k1)
group571 = ECGroup(sect571k1)

g256 = group256.random(G)
h256 = group256.random(G)

#Cofactor is 4 
#TODO: Just doing 8 change to 4 
g283 = (group283.random(G)) ** (group283.init(ZR, int(4)))
h283 = (group283.random(G)) ** (group283.init(ZR, int(4)))

g571 = (group571.random(G)) ** (group571.init(ZR, int(4)))
h571 = (group571.random(G)) ** (group571.init(ZR, int(4)))

decoded_g256 = group256.decode(g256)
decoded_h256 = group256.decode(h256)

decoded_g283 = group283.decode(g283)
decoded_h283 = group283.decode(h283)

decoded_g571 = group571.decode(g571)
decoded_h571 = group571.decode(h571)

'''
print("decoded_g256:\n", decoded_g256)
print("decoded_h256:\n", decoded_h256)

print("decoded_g283:\n", decoded_g283)
print("decoded_h283:\n", decoded_h283)

print("decoded_g571:\n", decoded_g571)
print("decoded_h571:\n", decoded_h571)




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
    
    print("g:", g)
    print("a:", a)
    print("b:", b)
    print("c:", c)
    print("d:", d)
    print("D:", D)
    print("D1:", D1)
    if D == D1:
        print("Equal")
    else:
        print("Not Equal")


    #    print("order:", group571.order())
print("\n\n")
'''


g = g256
a = group256.random(ZR)
B = g ** a

start_exp256 = time.process_time()
for i in range(1000):
    A = g ** a
end_exp256 = time.process_time()
total_time_exp256 = ( end_exp256 - start_exp256 ) * 1000


b = group256.random(ZR)
start_mul256 = time.process_time()
for i in range(1000):
    A = a * b 
end_mul256 = time.process_time()
total_time_mul256 = ( end_mul256 - start_mul256 ) * 1000


start_rand256 = time.process_time()
for i in range(1000):
    b = group256.random(ZR)
end_rand256 = time.process_time()
total_time_rand256 = ( end_rand256 - start_rand256 ) * 1000

b = group256.random(G)
start_ser256 = time.process_time()
for i in range(1000):
    bs = group256.serialize(b)
end_ser256 = time.process_time()
total_time_ser256 = ( end_ser256 - start_ser256 ) * 1000



g = g283
a = group283.random(ZR)
B = g ** a

start_exp283 = time.process_time()
for i in range(1000):
    A = g ** a
end_exp283 = time.process_time()
total_time_exp283 = ( end_exp283 - start_exp283 ) * 1000



b = group283.random(ZR)
start_mul283 = time.process_time()
for i in range(1000):
    A = a * b 
end_mul283 = time.process_time()
total_time_mul283 = ( end_mul283 - start_mul283 ) * 1000



start_rand283 = time.process_time()
for i in range(1000):
    b = group283.random(ZR)
end_rand283 = time.process_time()
total_time_rand283 = ( end_rand283 - start_rand283 ) * 1000


g = g571
a = group571.random(ZR)
B = g ** a

start_exp571 = time.process_time()
for i in range(1000):
    A = g ** a
end_exp571 = time.process_time()


total_time_exp571 = ( end_exp571 - start_exp571 ) * 1000

b = group571.random(ZR)
start_mul571 = time.process_time()
for i in range(1000):
    A = a * b 
end_mul571 = time.process_time()
total_time_mul571 = ( end_mul571 - start_mul571 ) * 1000

start_rand571 = time.process_time()
for i in range(1000):
    b = group571.random(ZR)
end_rand571 = time.process_time()
total_time_rand571 = ( end_rand283 - start_rand283 ) * 1000



print("Total time for 1000 256 bit exponentions:", total_time_exp256)
print("Total time for 1000 283 bit exponentions:", total_time_exp283)
print("Total time for 1000 571 bit exponentions:", total_time_exp571)
print("\n")
print("Total time for 1000 256 bit multiplications :", total_time_mul256)
print("Total time for 1000 283 bit multiplications :", total_time_mul283)
print("Total time for 1000 571 bit multiplications :", total_time_mul571)
print("\n")
print("Total time for 1000 256 bit random number generations:", total_time_rand256)
print("Total time for 1000 283 bit random number generations:", total_time_rand283)
print("Total time for 1000 571 bit random number generations:", total_time_rand256)
print("\n")
print("Total time for 1000 256 bit serializations:", total_time_ser256)
