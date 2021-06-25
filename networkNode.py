from operator import ne
import sys
import uuid
from flask import Flask
from flask import request
from flask.json import jsonify
from flask_restful import Resource, Api
from blockchain import Blockchain

bitcoin = Blockchain()
nodeAddress = str(uuid.uuid1()).replace('-','')

app = Flask(__name__)
api = Api(app)

@app.route('/blockchain', methods=['GET'])
def blk():
    return jsonify(bitcoin.serializer)

@app.route('/transaction', methods=['POST'])
def addTransaction():
    newTransaction = bitcoin.createNewTransaction(request.json['amount'], request.json['sender'], request.json['recipient'])
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
    newTransaction = bitcoin.createNewTransaction(12.5, '00', nodeAddress)
    newBlock = bitcoin.createNewBlock(nonce, previousBlockHash, blockHash)
    bitcoin.addTransactionToPendingTransaction(newTransaction)
    return {
            'note' : "New block mined and broadcast successfully.",
            'block' : newBlock
    }


if __name__ == '__main__':
    app.run(port=str(sys.argv[1]), debug=True)