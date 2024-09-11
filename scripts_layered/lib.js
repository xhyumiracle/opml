const fs = require("fs")
const rlp = require('rlp')
const child_process = require("child_process")

const basedir = process.env.BASEDIR == undefined ? "/tmp/cannon" : process.env.BASEDIR
const programPath = process.env.PROGRAM_PATH
const modelPath = process.env.MODEL_PATH
const modelName = process.env.MODEL_NAME
const dataPath = process.env.DATA_PATH
const prompt = process.env.PROMPT

async function deploy() {
  const MIPS = await ethers.getContractFactory("MIPS")
  const m = await MIPS.deploy()
  const mm = await ethers.getContractAt("MIPSMemory", await m.m())

  let startTrie = JSON.parse(fs.readFileSync(basedir + "/checkpoint/0_golden.json"))
  let goldenRoot = startTrie["root"]
  console.log("goldenRoot is", goldenRoot)

  const Challenge = await ethers.getContractFactory("LayeredChallenge")
  const c = await Challenge.deploy(m.address, goldenRoot)

  return [c, m, mm]
}

function getBlockRlp(block) {
  let dat = [
    block['parentHash'],
    block['sha3Uncles'],
    block['miner'],
    block['stateRoot'],
    block['transactionsRoot'],
    block['receiptsRoot'],
    block['logsBloom'],
    block['difficulty'],
    block['number'],
    block['gasLimit'],
    block['gasUsed'],
    block['timestamp'],
    block['extraData'],
    block['mixHash'],
    block['nonce'],
  ];
  // post london
  if (block['baseFeePerGas'] !== undefined) {
    dat.push(block['baseFeePerGas'])
  }
  dat = dat.map(x => (x == "0x0") ? "0x" : x)
  //console.log(dat)
  let rdat = rlp.encode(dat)
  if (ethers.utils.keccak256(rdat) != block['hash']) {
    throw "block hash doesn't match"
  }
  return rdat
}

async function deployed() {
  let addresses = JSON.parse(fs.readFileSync(basedir + "/deployed.json"))
  const c = await ethers.getContractAt("LayeredChallenge", addresses["LayeredChallenge"])
  const m = await ethers.getContractAt("MIPS", addresses["MIPS"])
  const mm = await ethers.getContractAt("MIPSMemory", addresses["MIPSMemory"])
  return [c, m, mm]
}

class MissingHashError extends Error {
  constructor(hash, offset) {
    super("hash is missing")
    this.hash = hash
    this.offset = offset
  }
}

async function getTrieNodesForCall(c, caddress, cdat, preimages) {
  let nodes = []
  while (1) {
    try {
      // TODO: make this eth call?
      // needs something like initiateChallengeWithTrieNodesj
      let calldata = c.interface.encodeFunctionData("callWithTrieNodes", [caddress, cdat, nodes])
      ret = await ethers.provider.call({
        to: c.address,
        data: calldata
      });
      break
    } catch (e) {
      let missing = e.toString().split("'")[1]
      if (missing == undefined) {
        // other kind of error from HTTPProvider
        missing = e.error.message.toString().split("execution reverted: ")[1]
      }
      if (missing !== undefined && missing.length == 64) {
        console.log("requested node", missing)
        let node = preimages["0x" + missing]
        if (node === undefined) {
          throw ("node not found")
        }
        const bin = Uint8Array.from(Buffer.from(node, 'base64').toString('binary'), c => c.charCodeAt(0))
        nodes.push(bin)
        continue
      } else if (missing !== undefined && missing.length == 128) {
        let hash = missing.slice(0, 64)
        let offset = parseInt(missing.slice(64, 128), 16)
        console.log("requested hash oracle", hash, offset)
        throw new MissingHashError(hash, offset)
      } else {
        console.log(e)
        break
      }
    }
  }
  return nodes
}

function getTrieAtStep(step, nodeID, isLastLayer) {
  let fn = basedir + "/checkpoint" + "/checkpoint_" + nodeID.toString() + "_" + step.toString() + ".json"
  if (step == -1) {
    fn = basedir + "/checkpoint" + "/checkpoint_" + nodeID.toString() + "_final" + ".json"
  }
  if (!isLastLayer) {
    fn = basedir + "/checkpoint" + "/" + nodeID.toString() + "_golden" + ".json"
  }

  if (!fs.existsSync(fn)) {
    // console.log("running mipsevm")
    console.log("running program: ", programPath)
    const inputPath = basedir + "/data/node_" + nodeID.toString()
    const lastLayer = isLastLayer ? " --lastLayer" : " "
    const command = "mlvm/mlvm" + lastLayer + " --target=" + step.toString() + " --program=" + programPath + " --modelName=" + modelName + " --data=" + inputPath + " --nodeID=" + nodeID.toString() + " --model=" + modelPath + " --prompt=" + prompt
    console.log(command)
    child_process.execSync(command, { stdio: 'inherit' })

  }

  return JSON.parse(fs.readFileSync(fn))
}


async function writeMemory(mm, root, addr, data, bytes32 = false) {
  if (bytes32) {
    ret = await mm.WriteBytes32WithReceipt(root, addr, data)
  } else {
    ret = await mm.WriteMemoryWithReceipt(root, addr, data)
  }
  const receipt = await ret.wait()
  for (l of receipt.logs) {
    if (l.topics[0] == "0x86b89b5c9818dbbf520dd979a5f250d357508fe11b9511d4a43fd9bc6aa1be70") {
      root = l.data
    }
  }
  console.log("new hash", root)
  return root
}

module.exports = { basedir, deploy, deployed, getTrieNodesForCall, getBlockRlp, getTrieAtStep, writeMemory, MissingHashError }
