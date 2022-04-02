def check_power_of_3(n):
    while (n % 3 == 0): 
        n = n/3 
    return n==1 

def maj3_ind(l1, l2,l3):
    ind_list = l1+l2 + l1+l3 + l2+l3
    return ind_list 

def maj3_tree_root_index_list(N):
    if not check_power_of_3(N):
        print("N not a power of 3")
        return 
    lol  = [[x] for x in range(N)]    # lol - list of lists :)
    #print(lol)
    while(len(lol) > 1):
        temp_list = []
        for i in range(len(lol)//3):
            temp_list.append( maj3_ind( lol[3*i], lol[3*i + 1],lol[3*i +2]))
            #print(temp_list)
        lol = temp_list
    return lol[0]

if __name__ == "__main__":
    print(maj3_tree_root_index_list(3))
    print(maj3_tree_root_index_list(9))
