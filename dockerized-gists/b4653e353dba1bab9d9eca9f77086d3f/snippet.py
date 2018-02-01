from web3 import Web3, HTTPProvider

web3 = Web3(HTTPProvider("http://localhost:8545"))

PERCENTILE = 0.6
NUMBLOCKS = 43200
# NUMBLOCKS = 1000

def getMinGasPrice(block):
    minPrice = None
    for tx in block.transactions:
        if tx['from'] == block.miner: continue
        if minPrice is None or tx.gasPrice < minPrice:
            minPrice = tx.gasPrice
    return minPrice

def gpo(minPrices, percentile):
    minPrices = sorted(price for price in minPrices if price)
    return minPrices[int(len(minPrices) * percentile)]

def main():
  endBlock = web3.eth.blockNumber
  startBlock = web3.eth.blockNumber - NUMBLOCKS

  minprices = []
  estimates = []
  delayBlocks = 0
  overpayments = []
  minedCount = 0
  for blocknum in range(startBlock, endBlock):
      if blocknum % 100 == 0:
          print "Processing block %d" % (blocknum,)
          overpayments.sort()
          if minedCount > 0:
              print "  Average latency: %.2f blocks" % (delayBlocks / float(minedCount),)
              print "  Median overpayment: %d%%" % (overpayments[len(overpayments) / 2] * 100,)
      block = web3.eth.getBlock(blocknum, full_transactions=True)
      minprice = getMinGasPrice(block)
      if minprice:
          # 'mine' any previous estimates that could have been included
          # in this block.
          for i in range(len(estimates) - 1, -1, -1):
              if estimates[i][1] >= minprice:
                  overpayments.append((estimates[i][1] / float(minprice)) - 1)
                  delayBlocks += blocknum - estimates[i][0]
                  minedCount += 1
                  del estimates[i]

      minprices.append(minprice)
      # Get a new oracle estimate
      if len(minprices) >= 100:
          minprices = minprices[-100:]
          gasPrice = gpo(minprices, PERCENTILE)
          estimates.append((blocknum, gasPrice))

  print "Unmined transactions: %d" % (len(estimates),)
  print "Average latency: %.2f blocks" % (delayBlocks / float(minedCount),)
  overpayments.sort()
  print "Median overpayment: %d%%" % (overpayments[len(overpayments) / 2] * 100,)

if __name__ == '__main__':
  main()
