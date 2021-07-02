'''
Author : Mukesh Dasari
Last Modified : 07-01-2021
Description : This file contains the flask server creation and all apis which are required
to access/modify our blockchain network 

'''

# Importing all the required dependencies
import sys
import uuid
from flask import Flask
from flask import request
from flask import json
from flask.json import jsonify
from flask_restful import Api
from blockchain import Blockchain
import requests

bitcoin = Blockchain()      # Object creation of Blockchain class
nodeAddress = str(uuid.uuid1()).replace('-','')     # Creating one unique random address (wallet) for our currrent host node 

app = Flask(__name__)
api = Api(app)

# This is get api to fetch the whole blockchain data
@app.route('/blockchain', methods=['GET'])
def blk():
    return jsonify(bitcoin.serializer)

# This api will only add the transaction data sent in body to blockchain's pending transactions list
@app.route('/transaction', methods=['POST'])
def addTransaction():
    newTransaction = request.json
    blockIndex = bitcoin.addTransactionToPendingTransaction(newTransaction)
    return jsonify({'note' : 'Transaction will be added in block' + str(blockIndex)})

# This api will call proof of work function i.e mining
# Once we get our nonce we create and broadcast one new transaction with amount 12.5 which are 
# mined bicoins and rewarded to the current node (who has mined the block)
@app.route('/mine', methods=['GET'])
def mine():
    previousBlock = bitcoin.getLastBlock()
    previousBlockHash = previousBlock['hash']
    currentBlockData = {
        'transactions' : bitcoin.pendingTransactions,
        'index' : previousBlock['index'] + 1
    }
    nonce = bitcoin.proofOfWork(previousBlockHash, currentBlockData)
    blockHash = bitcoin.hashBlock(previousBlockHash, currentBlockData, nonce)
    newBlock = bitcoin.createNewBlock(nonce, previousBlockHash, blockHash)
    for network in bitcoin.networkNodes:
        requests.post(network + "/receive-new-block", json=newBlock)

    requests.post(bitcoin.currentNodeUrl + "/transaction/broadcast", json={"amount":12.5, "sender":"00", "recipient":nodeAddress})

    return {
            'note' : "New block mined and broadcast successfully.",
            'block' : newBlock
    }

# This api will only register the sent node with current node
@app.route('/register-node', methods=['POST'])
def registerNewNode():
    newNodeUrl = request.json['newNodeUrl']
    if(bitcoin.networkNodes.__contains__(newNodeUrl) == False and bitcoin.currentNodeUrl != newNodeUrl):
        bitcoin.networkNodes.append(newNodeUrl)
        return {'note' : "New node registered successfully with node."}
    else:
        return {'note' : "This node can not be registered."}
    
# This api will register bulk of nodes with current node
@app.route('/register-node-bulk', methods=['POST'])
def registerBulkNodes():
    allNetworkNodes = request.json['allNetworkNodes']
    declinedNodes = []
    for node in allNetworkNodes:
        if(bitcoin.networkNodes.__contains__(node) == False and bitcoin.currentNodeUrl != node):
            bitcoin.networkNodes.append(node)
        else:
            declinedNodes.append(node)
    if(declinedNodes.__len__() == 0):
        return {'note' : "All nodes registered successfully with node."}
    else:
        response = "Given node can not be registered."
        for node in declinedNodes:
            response = response + node + " "
        return {'note' : response}

# This function will register the sent node with current as well as with all other nodes
# who are part of our blockchain network
@app.route('/register-and-broadcast-node', methods=['POST'])
def registerAndBroadcastNode():
    newNodeUrl = request.json["newNodeUrl"]
    if(bitcoin.networkNodes.__contains__(newNodeUrl) == False and bitcoin.currentNodeUrl != newNodeUrl):
        bitcoin.networkNodes.append(newNodeUrl)
    for network in bitcoin.networkNodes:
        networkNodes = list(bitcoin.networkNodes)
        networkNodes.append(bitcoin.currentNodeUrl)
        requests.post(network+"/register-node-bulk", json={'allNetworkNodes' : networkNodes})

    return {"note" : "New node registerd with network successfully."}

# This api is internally used by mine in which we append the new block to blockchain
@app.route('/receive-new-block', methods=['POST'])
def receiveNewBlock():
    newBlock = request.json
    lastBlock = bitcoin.getLastBlock()
    correctHash = lastBlock['hash'] == newBlock['previousBlockHash']
    correctIndex = lastBlock['index'] + 1 == newBlock['index']
    if(correctHash and correctIndex):
        bitcoin.chain.append(newBlock)
        bitcoin.pendingTransactions = []
        return {
            "note" : "New block received and accepted.",
            "newBlock" : newBlock
        }
    else:
        return {
            "note" : "New block rejected",
            "newBlock" : newBlock
        }

# This api will create new transaction and also broadcast to all other nodes 
# who are part of our blockchain network
@app.route('/transaction/broadcast', methods=['POST'])
def transactionBroadcast():
    newTransaction = bitcoin.createNewTransaction(request.json['amount'], request.json['sender'], request.json['recipient'])
    bitcoin.addTransactionToPendingTransaction(newTransaction)

    for network in bitcoin.networkNodes:
        requests.post(network+"/transaction", json=newTransaction)

    return {"note" : "Transaction created and broadcasted successfully."}

# This api will make sure all the nodes are referring the same blockchain
# Being on distributed network if node is joined very recently then that node 
# can take a copy of the longest chain from the blockchain network
@app.route('/consensus', methods=['GET'])
def chainConsensus():
    blockchains = []
    for network in bitcoin.networkNodes:
        blockchainResponse = requests.get(network + '/blockchain')
        blockchains.append(json.loads(blockchainResponse.text))
    currentChainLength = len(bitcoin.chain)
    maxChainLength = currentChainLength
    newLongestChain = None
    newPendingTransactions = None
    for blockchain in blockchains:
        if(len(blockchain['chain']) > maxChainLength):
            maxChainLength = len(blockchain['chain'])
            newLongestChain = blockchain['chain']
            newPendingTransactions = blockchain['pendingTransactions']
        
    if(newLongestChain == None or (newLongestChain and bitcoin.chainIsValid(newLongestChain) == False)):
        return {
            "note" : 'Current chain has not been replaced.',
            "chain" : bitcoin.chain
        }
    elif(newLongestChain and bitcoin.chainIsValid(newLongestChain)):
        bitcoin.chain = newLongestChain
        bitcoin.pendingTransactions = newPendingTransactions
        return {
            "note" : 'This chain has replaced.',
            "chain" : bitcoin.chain
        }

if __name__ == '__main__':
    # Running the server
    app.run(port=str(sys.argv[1]), debug=True)