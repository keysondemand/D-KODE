## D-KODE 

**Protocol to generate secret keys on-the-fly using key-homomorphic PRFs and black-box secret sharing** 

**Requirements:**

Charm crypto library: https://github.com/JHUISI/charm

Tendermint: https://tendermint.com/ 

**To test the code locally:**

1. Install Tendermint
2. Run tendermint with kvstore app using `tendermint node --proxy_app=kvstore`

First check secret sharing:
Navigate to secretsharing/blackbox/ and run `python3 bbss.py`.
It runs a black-box secret sharing for a default of 4 nodes. 
For any other number of nodes, try `python3 bbss.py -n <number of nodes>`

*For Shamir secret sharing:*

Navigate to secretsharing/shamir and run `python3 shamirsharing.py -n <number of nodes>`. The default is 4 nodes.
  
*For Combinatorial/Replicated secret sharing:*

Navigate to secretsharing/combinatorial and run `python3 css.py -n <number of nodes>`. The default is 4 nodes. 


*To check the distributed key generation code:*
Run `sh bbss_dkg_run.sh <number of nodes>`. This script runs only for MAC OSX. 

Other DKGs using Shamir secret sharing, Replicated secret sharing can be run using 

`sh shamir_dkg_run.sh <number of nodes>`

`sh css_dkg_run.sh <number of nodes>`


**Note:**
1. The current code queries or posts transactions on the port `46657`, depending on the version of tendermint, the port may have to be changed in the file
`util/transactionbroadcast.py`to either `26657` or other configured port

2. The majority of code for node can be found in `util/node_functions.py`



