from os import get_terminal_size
import sys
import hashlib
import uuid
from datetime import datetime

from flask.app import Flask

currentNodeUrl = str(sys.argv[2])

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pendingTransactions = []
        self.currentNodeUrl = currentNodeUrl
        self.networkNodes = []
        self.createNewBlock(100, '0','0')

    @property
    def serializer(self):
        return {
            'chain' : self.chain,
            'pendingTransactions' : self.pendingTransactions,
            'currentNodeUrl' : self.currentNodeUrl,
            'networkNodes' : self.networkNodes
        }
        
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

    def getLastBlock(self):
        return self.chain[len(self.chain)-1]

    def createNewTransaction(self, amount, sender, recipient):
        newTransaction = {
            "amount":amount,
            "recipient":recipient,
            "sender":sender,           
            "transactionId":str(uuid.uuid1()).replace('-','')
        }
        return newTransaction

    def addTransactionToPendingTransaction(self, transactionObj):
        self.pendingTransactions.append(transactionObj)
        return self.getLastBlock()['index']+1

    def hashBlock(self, previousBlockHash, currentBlockData, nonce):
        dataAsString = previousBlockHash + str(nonce) + str(currentBlockData)
        hash = hashlib.sha256(dataAsString.encode('utf-8')).hexdigest()
        return hash

    def proofOfWork(self, previousBlockHash, currentBlockData):
        nonce = 0
        hash = self.hashBlock(previousBlockHash, currentBlockData, nonce)
        while(hash[0:4] != "0000"):
            nonce = nonce + 1
            hash = self.hashBlock(previousBlockHash, currentBlockData, nonce)
        return nonce

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
    


    
