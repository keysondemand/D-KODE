def number_iter(start_p, delta, n):
    power = 4
    count = 0
    p = start_p + delta 
    '''
    #while (p< (1- 2**(-n))):
    if (p > (1- 2**(-1*n))):
        return 1
    '''
    while (p< (1- 2**(-1*power))):
        count = count + 1
        p = (3*(1-p)*(p**2)) + (p**3) 
    return count 

def number_iter2(start_p, delta, n):
    count = 0
    p = start_p + delta 
    power = n / 4 

    if n <= 20:
        while (p< (1- 2**(-1*power))):
            count = count + 1
            p = (3*(1-p)*(p**2)) + (p**3) 
    else:
        while (p< (1- 2**(-1*power))):
            count = count + 1
            p = (3*(1-p)*(p**2)) + (p**3) 

    return count 

if __name__ == "__main__":
    for n in [5, 10,  20, 30, 40, 60]:
        for start_p in [0.5, 0.66]:

            delta = (1/n)
            count = number_iter2(start_p, delta, n)
            print("n",n, "start_p:", start_p, "m:",3**count)
    
        #req_threshold = ((2*n)//3) + 1
        #start_p = req_threshold / n
        #delta = (1/n)
        #count = number_iter2(start_p, delta, n)
        #print("n",n, "start_p:", start_p, "m:",3**count)
