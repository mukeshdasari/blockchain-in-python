from operator import contains, ne
import sys
import uuid
from flask import Flask
from flask import request
from flask import json
from flask.cli import routes_command
from flask.json import jsonify
from flask_restful import Api, abort
from blockchain import Blockchain
import requests

bitcoin = Blockchain()
nodeAddress = str(uuid.uuid1()).replace('-','')

app = Flask(__name__)
api = Api(app)

@app.route('/blockchain', methods=['GET'])
def blk():
    return jsonify(bitcoin.serializer)

@app.route('/transaction', methods=['POST'])
def addTransaction():
    newTransaction = request.json
    blockIndex = bitcoin.addTransactionToPendingTransaction(newTransaction)
    return jsonify({'note' : 'Transaction will be added in block' + str(blockIndex)})

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
    # newTransaction = bitcoin.createNewTransaction(12.5, '00', nodeAddress)
    newBlock = bitcoin.createNewBlock(nonce, previousBlockHash, blockHash)
    for network in bitcoin.networkNodes:
        requests.post(network + "/receive-new-block", json=newBlock)

    requests.post(bitcoin.currentNodeUrl + "/transaction/broadcast", json={"amount":12.5, "sender":"00", "recipient":nodeAddress})

    return {
            'note' : "New block mined and broadcast successfully.",
            'block' : newBlock
    }

@app.route('/register-node', methods=['POST'])
def registerNewNode():
    newNodeUrl = request.json['newNodeUrl']
    if(bitcoin.networkNodes.__contains__(newNodeUrl) == False and bitcoin.currentNodeUrl != newNodeUrl):
        bitcoin.networkNodes.append(newNodeUrl)
        return {'note' : "New node registered successfully with node."}
    else:
        return {'note' : "This node can not be registered."}
    
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

@app.route('/transaction/broadcast', methods=['POST'])
def transactionBroadcast():
    newTransaction = bitcoin.createNewTransaction(request.json['amount'], request.json['sender'], request.json['recipient'])
    bitcoin.addTransactionToPendingTransaction(newTransaction)

    for network in bitcoin.networkNodes:
        requests.post(network+"/transaction", json=newTransaction)

    return {"note" : "Transaction created and broadcasted successfully."}


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
        # print(len(blockchain['chain']))
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
    app.run(port=str(sys.argv[1]), debug=True)