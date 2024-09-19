const fs = require("fs")
const { getTrieAtStep } = require("./lib")
const child_process = require("child_process")

const basedir = process.env.BASEDIR == undefined ? "/tmp/cannon" : process.env.BASEDIR
const logdir = process.env.LOGDIR == undefined ? "logs/stats" : process.env.LOGDIR

function _logMIPSSteps(nodeID, mipsSteps, stdout, logFile) {

  let logstr = "layer nodeID: " + nodeID.toString() + " rest mips step: " + mipsSteps

  fs.appendFileSync(logFile, stdout, (err) => {
    if (err) {
      console.error('Error writing to file:', err);
    } else {
      console.log('File written successfully:', logFile);
    }
  });
  fs.appendFileSync(logFile, logstr, (err) => {
    if (err) {
      console.error('Error appending to file:', err);
    } else {
      console.log('File appended successfully:', logFile);
    }
  });
  console.log(logstr);
}

async function getMIPSSteps(nodeID, logFile) {
  return new Promise((resolve, reject) => {
    let execCb = (error, stdout, stderr, finalTrie) => {
      if (error) {
        console.error(`Error in node ${nodeID}:`, error);
        return reject(error);  // Notify the promise of an error
      }

      mipsSteps = finalTrie['step'];
      _logMIPSSteps(nodeID, mipsSteps, stdout, logFile)
      // console.log(`Node ${nodeID}:`, stdout);
      // console.err(`Node ${nodeID} stderr:`, stderr);
      resolve()
    }

    console.log("gen startTrie for nodeID =", nodeID)
    // exec sync
    let startTrie = getTrieAtStep(nodeID, nodeID, false, " --outputMode=2 ", true, null, logFile)
    console.log("gen finalTrie for nodeID =", nodeID)
    // exec async (with execCb provided)
    getTrieAtStep(-1, nodeID, true, " --outputMode=2 ", true, execCb)
  })
}

// need /checkpoint/0_golden.json before execute
function getNodeCount() {
  let finalTrie = JSON.parse(fs.readFileSync(basedir + "/checkpoint/0_golden.json"))
  return finalTrie['nodeCount']
}

let MAX_THREADS = 12

function clearData(data_dir) {
  child_process.execSync('rm -rf ' + data_dir + '/data/node_*', (error, stdout, stderr) => {
  })
}

async function main() {

  const tasks = []
  // total layer node counts?
  let nodeCount = getNodeCount();
  // let nodeCount = 10
  console.log("total layer node count:", nodeCount);
  // get mips steps from layer nodeID to final step
  for (let i = nodeCount - 1; i >= 0; i--) {
    // if (i > 981) continue // nodeID filter
    if (i % MAX_THREADS == 0) {
      console.log("Meet a batch tasks:", i)
      await Promise.all(tasks)
      clearData(basedir)
    }
    let logFile = logdir + '/' + process.env.MODEL_NAME + '/node_' + i.toString() + '.log'
    // tasks.push(async.apply(getMIPSSteps, i, logFile))
    tasks.push(getMIPSSteps(i, logFile))
  }
  await Promise.all(tasks)
  clearData(basedir)
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });