'''
Author : Mukesh Dasari
Last Modified : 07-01-2021
Descrition : This file contains the structure of blockchain network and
all the operations required to perform on it

'''

# Importing all the required dependencies
from logging import error
import sys
import hashlib
import uuid
from datetime import datetime

currentNodeUrl = None       # Current host url

if(len(sys.argv) != 3):     # Checking if all the parameters are passed
    error('Invalid inputs!')
    error('Usage : python networkNode.py port host')
    sys.exit(0)             # Terminating of execution
else:
    currentNodeUrl = str(sys.argv[2])

# This class provides structure and utilities functions to work with Blockchain network 
class Blockchain:
    def __init__(self):                         # Initializing the class
        self.chain = []                         # This will contains the actual mined blocks
        self.pendingTransactions = []           # Before mining all the transactions are stored in this
        self.currentNodeUrl = currentNodeUrl    # Current host url
        self.networkNodes = []                  # List of all the nodes which are part of distributed blockchain network
        self.createNewBlock(100, '0','0')       # Creating the intial genesis block which will be the stating block of our chain 

    @property      # Creating property decorator which will represent our blockchain data             
    def serializer(self):
        return {
            'chain' : self.chain,
            'pendingTransactions' : self.pendingTransactions,
            'currentNodeUrl' : self.currentNodeUrl,
            'networkNodes' : self.networkNodes
        }
    
    # This function will create new block with provided nonce, previous block hash and current block hash
    # It will assign index to block and timestamp at which block has been created. 
    # Then it will append block to our main blockchain chain and reinitialize the pending transactions as those are 
    # added in the block's transactions and it will return the new block
    def createNewBlock(self, nonce, previousBlockHash, hash):
        newBlock = {
            "index" : len(self.chain)+1,
            "timestamp" : str(datetime.now()),
            "transactions" : self.pendingTransactions,
            "nonce" : nonce,
            "hash" : hash,
            "previousBlockHash" : previousBlockHash
        }
        self.pendingTransactions = []
        self.chain.append(newBlock)
        return newBlock

    # This function will simply return last block of our blockchin
    def getLastBlock(self):
        return self.chain[len(self.chain)-1]

    # New transaction object is created and a transaction id is assigned to it
    def createNewTransaction(self, amount, sender, recipient):
        newTransaction = {
            "amount":amount,
            "recipient":recipient,
            "sender":sender,           
            "transactionId":str(uuid.uuid1()).replace('-','')
        }
        return newTransaction

    # This will add the provided transaction object to pending transactions list
    def addTransactionToPendingTransaction(self, transactionObj):
        self.pendingTransactions.append(transactionObj)
        return self.getLastBlock()['index']+1

    # This function will create hash of block's data using SHA256 algorithm
    def hashBlock(self, previousBlockHash, currentBlockData, nonce):
        dataAsString = previousBlockHash + str(nonce) + str(currentBlockData)
        hash = hashlib.sha256(dataAsString.encode('utf-8')).hexdigest()
        return hash

    # This function finds the nonce which satisfies the condition of hash 
    # In our case we find untill our hash starts with 0000
    def proofOfWork(self, previousBlockHash, currentBlockData):
        nonce = 0
        hash = self.hashBlock(previousBlockHash, currentBlockData, nonce)
        while(hash[0:4] != "0000"):
            nonce = nonce + 1
            hash = self.hashBlock(previousBlockHash, currentBlockData, nonce)
        return nonce

    # This function finds whether the passed blockchain is valid or not
    # We check each block's hash and its previous block hash to check whether any block is tampered or not 
    def chainIsValid(self, blockchain):
        validChain = True
        for i in range(1, len(blockchain)):
            currentBlock = blockchain[i]
            prevBlock = blockchain[i-1]
            blockHash = self.hashBlock(prevBlock['hash'], {"transactions" : currentBlock['transactions'], "index" : currentBlock['index']}, currentBlock['nonce'])
            
            if(blockHash[0:4] != "0000"):
                validChain = False
            if(currentBlock['previousBlockHash'] != prevBlock['hash']):
                validChain = False
        
        genesisBlock = blockchain[0]
        currentNonce = genesisBlock['nonce'] == 100
        correctPreviousBlockHash = genesisBlock['previousBlockHash'] == '0'
        correctHash = genesisBlock['hash'] == '0'
        correctTransactions = len(genesisBlock['transactions']) == 0

        if(currentNonce == False or correctPreviousBlockHash == False or correctHash == False or correctTransactions == False):
            validChain = False
        
        return validChain
    


    
