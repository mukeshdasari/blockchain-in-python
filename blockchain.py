import sys
import hashlib
import uuid
from datetime import datetime

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
            "timestamp" : datetime.now(),
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
            "sender":sender,
            "recipient":recipient,
            "transactionId":str(uuid.uuid1()).replace('-','')
        }
        return newTransaction

    def addTransactionToPendingTransaction(self, transactionObj):
        print(transactionObj)
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

    
