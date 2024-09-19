package vm

import (
	"bytes"
	"encoding/binary"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strconv"

	"github.com/ethereum/go-ethereum/common"
	uc "github.com/unicorn-engine/unicorn/bindings/go/unicorn"

	"mlvm/timer"
)

func WriteCheckpoint(ram map[uint32](uint32), fn string, step int, briefMode int) {
	timer.StartTimer("gentrie")

	trieroot := common.Hash{} // set all 0 when is brief
	if briefMode <= 1 {
		trieroot = RamToTrie(ram)
	}

	timer.StopTimer("gentrie")

	timer.StartTimer("writefile")

	dat := TrieToJson(trieroot, step, briefMode == 0)
	fmt.Printf("writing %s len %d with root %s\n", fn, len(dat), trieroot)
	ioutil.WriteFile(fn, dat, 0644)

	timer.StopTimer("writefile")
}

// isBrief: for benchmark, no need to write ram
func WriteCheckpointWithNodeID(ram map[uint32](uint32), fn string, step int, nodeID int, nodeCount int, briefMode int) {
	timer.StartTimer("gentrie")

	trieroot := common.Hash{} // set all 0 when is brief
	if briefMode <= 1 {
		trieroot = RamToTrie(ram)
	}

	timer.StopTimer("gentrie")

	timer.StartTimer("writefile")

	dat := TrieToJsonWithNodeID(trieroot, step, nodeID, nodeCount, briefMode == 0)
	fmt.Printf("writing %s len %d with root %s\n", fn, len(dat), trieroot)
	ioutil.WriteFile(fn, dat, 0644)

	timer.StopTimer("writefile")
}

// memory layout in MIPS
const (
	INPUT_ADDR  = 0x31000000
	OUTPUT_ADDR = 0x32000000
	MODEL_ADDR  = 0x33000000
	MAGIC_ADDR  = 0x30000800
)

const (
	MIPS_PROGRAM = "../../mlgo/ml_mips/ml_mips.bin"
)

const (
	READ_FROM_BIDENDIAN = true
	OUTPUT_TO_BIDENDIAN = true
)

func IntToBytes(n int) []byte {
	x := int32(n)
	bytesBuffer := bytes.NewBuffer([]byte{})
	if READ_FROM_BIDENDIAN {
		binary.Write(bytesBuffer, binary.BigEndian, x)
	} else {
		binary.Write(bytesBuffer, binary.LittleEndian, x)
	}

	return bytesBuffer.Bytes()
}

func LoadModel(mu uc.Unicorn, file string, ram map[uint32](uint32)) {

	timer.StartTimer("readmodel")

	modelBytes, err := ioutil.ReadFile(file)
	if err != nil {
		fmt.Println(err)
		return
	}
	modelSize := len(modelBytes)
	fmt.Println("modelSize: ", modelSize)
	rawSize := IntToBytes(modelSize)
	fmt.Println("rawSize: ", rawSize)

	timer.StopTimer("readmodel")

	timer.StartTimer("loadram-model")
	LoadBytesToUnicorn(mu, rawSize, ram, MODEL_ADDR)
	LoadBytesToUnicorn(mu, modelBytes, ram, MODEL_ADDR+4)
	timer.StopTimer("loadram-model")
}

func LoadInputData(mu uc.Unicorn, file string, ram map[uint32](uint32)) error {

	timer.StartTimer("readinput")

	// load a random test digit
	buf, err := ioutil.ReadFile(file)
	if err != nil {
		fmt.Println(err)
		return err
	}
	if len(buf) >= 10*1024*1024 {
		fmt.Println("data too large, but ignore")
		// fmt.Println("data too large, use 10*1024*1024")
		// buf = buf[:10*1024*1024]
		// return errors.New("data too large")
	}
	timer.StopTimer("readinput")

	timer.StartTimer("loadram-input")
	//buf is the data
	inputSize := len(buf)
	LoadBytesToUnicorn(mu, IntToBytes(inputSize), ram, INPUT_ADDR)
	LoadBytesToUnicorn(mu, buf, ram, INPUT_ADDR+4)

	timer.StopTimer("loadram-input")

	return nil
}

type Params struct {
	Target       int
	ProgramPath  string
	ModelPath    string
	InputPath    string
	Basedir      string
	OutputGolden bool
	// NoOutputGolden  bool
	OutputMode int

	CurLayer  int
	LastLayer bool
	ModelName string
	NodeID    int

	MIPSVMCompatible bool
	Prompt           string
	PeekGraph        bool
	OutputBenchmark  bool
}

func ParseParams() *Params {
	var target int
	var programPath string
	var modelPath string
	var inputPath string
	var basedir string
	var outputGolden bool
	// var noOutputGolden bool
	var outputMode int

	var curLayer int
	var lastLayer bool
	var modelName string
	var nodeID int

	var mipsVMCompatible bool
	var prompt string

	var peekGraph bool
	var outputBenchmark bool

	defaultBasedir := os.Getenv("BASEDIR")
	if len(defaultBasedir) == 0 {
		defaultBasedir = "/tmp/cannon"
	}
	flag.StringVar(&basedir, "basedir", defaultBasedir, "Directory to read inputs, write outputs, and cache preimage oracle data.")
	flag.IntVar(&target, "target", -1, "Target number of instructions to execute in the trace. If < 0 will execute until termination")
	flag.StringVar(&programPath, "program", MIPS_PROGRAM, "Path to binary file containing the program to run")
	flag.StringVar(&modelPath, "model", "", "Path to binary file containing the AI model")
	flag.StringVar(&inputPath, "data", "", "Path to binary file containing the input of AI model")
	flag.BoolVar(&outputGolden, "outputGolden", false, "Do not read any inputs and instead produce a snapshot of the state prior to execution. Written to <basedir>/golden.json")
	// flag.BoolVar(&noOutputGolden, "noOutputGolden", false, "suppress --outputGolden or any default output golden file actions")
	flag.IntVar(&outputMode, "outputMode", 0, "the level of **brief** for writing golden, checkpoint, final files; 0 - full checkpoints, with trie, 1 - only trie root, 2 - no gen trie, root 0x00..00.")

	flag.BoolVar(&lastLayer, "lastLayer", false, "In the lastLayer, we run computation in VM")
	flag.IntVar(&curLayer, "curLayer", 0, "The current layer")
	flag.StringVar(&modelName, "modelName", "MNIST", "run MNIST or LLAMA")
	flag.IntVar(&nodeID, "nodeID", 0, "The current nodeID")

	flag.BoolVar(&mipsVMCompatible, "mipsVMCompatible", false, "compatible for MIPS VM")
	flag.StringVar(&prompt, "prompt", "How to combine AI and blockchain?", "prompt for LLaMA")

	flag.BoolVar(&peekGraph, "peekGraph", false, "Print the scale of tensor compute graph for given params.")
	flag.BoolVar(&outputBenchmark, "outputBenchmark", false, "Print the performance benchamrk.")

	flag.Parse()

	params := &Params{
		Target:       target,
		ProgramPath:  programPath,
		ModelPath:    modelPath,
		InputPath:    inputPath,
		Basedir:      basedir,
		OutputGolden: outputGolden,
		// NoOutputGolden:   noOutputGolden,
		OutputMode:       outputMode,
		CurLayer:         curLayer,
		LastLayer:        lastLayer,
		ModelName:        modelName,
		NodeID:           nodeID,
		MIPSVMCompatible: mipsVMCompatible,
		Prompt:           prompt,
		PeekGraph:        peekGraph,
		OutputBenchmark:  outputBenchmark,
	}

	return params
}

func Run() {

	timer.StartTimer("total")

	params := ParseParams()
	timer.ENABLE = params.OutputBenchmark
	RunWithParams(params)

	timer.StopTimer("total")

	if params.OutputBenchmark {
		// timer calc & print
		totalTime, _ := timer.ConvertUint(timer.ElapsedTime("total"), "sec")
		sysIOTime, _ := timer.ConvertUint(timer.SumElapsedTimes([]string{"readmodel", "readmappedfile", "readinput", "writefile", "savedata", "stdout"}), "sec")
		vmIOTime, _ := timer.ConvertUint(timer.SumElapsedTimes([]string{"graph-node2bytes", "loadram-model", "loadram-input"}), "sec")
		vmExecTime, _ := timer.ConvertUint(timer.SumElapsedTimes([]string{"graph-compute", "gentrie", "uc-exec"}), "sec")
		// fmt.Println("totalTime:", totalTime)
		timer.PrintAllTimersWithUnit("sec")
		// timer.PrintAllTimers()
		nonIOTime := totalTime - sysIOTime
		fmt.Println("sysIOTime:", sysIOTime)
		fmt.Println("nonIOTime:", nonIOTime)
		fmt.Println("vmIOTime:", vmIOTime)
		fmt.Println("vmExecTime:", vmExecTime)
	}
}

func RunWithParams(params *Params) {

	target := params.Target
	programPath := params.ProgramPath
	modelPath := params.ModelPath
	inputPath := params.InputPath
	basedir := params.Basedir
	outputGolden := params.OutputGolden
	// noOutputGolden := params.NoOutputGolden
	outputMode := params.OutputMode
	// curLayer := params.CurLayer
	lastLayer := params.LastLayer
	modelName := params.ModelName
	nodeID := params.NodeID
	peekGraph := params.PeekGraph

	if peekGraph {
		graph, _, _ := GenGraph(modelName, nodeID, params.ModelPath, params.Prompt, params.InputPath)

		timer.StartTimer("stdout")

		PrintGraph(graph, modelName)

		timer.StopTimer("stdout")
	}

	if params.MIPSVMCompatible {
		MIPSRunCompatible(basedir, target, programPath, modelPath, inputPath, outputGolden, outputMode)
		return
	}

	if !lastLayer {
		id := target
		nodeFile, nodeCount, err := LayerRun(basedir+"/data", id, modelName, params)
		if err != nil {
			fmt.Println("layer run error: ", err)
			return
		}
		//xhyu: get the state at the beginning of this node id by target step = 0
		MIPSRun(basedir+"/checkpoint", 0, id, programPath, nodeFile, true, outputMode, nodeCount)
	} else {
		// the lastLayer
		MIPSRun(basedir+"/checkpoint", target, nodeID, programPath, inputPath, outputGolden, outputMode, 0)
	}

	// step 2 (optional), validate each 1 million chunk in EVM

	// step 3 (super optional) validate each 1 million chunk on chain

	//RunWithRam(ram, steps, debug, nil)

}

func LayerRun(basedir string, nodeID int, modelName string, params *Params) (string, int, error) {

	envBytes, nodeCount, err := GenGraphData(modelName, nodeID, params.ModelPath, params.Prompt, params.InputPath)

	if err != nil {
		fmt.Println("Layer run error: ", err)
		return "", nodeCount, err
	}

	timer.StartTimer("savedata")

	fileName := fmt.Sprintf("%s/node_%d", basedir, nodeID)
	fmt.Println("--------- in LayerRun, save data to:", fileName)
	err = saveDataToFile(envBytes, fileName)

	if err != nil {
		fmt.Println("Save data error: ", err)
		return fileName, nodeCount, err
	}

	timer.StopTimer("savedata")

	return fileName, nodeCount, nil
}

func saveDataToFile(data []byte, filename string) error {
	fout, err := os.Create(filename)
	if err != nil {
		fmt.Println(err)
		return err
	}
	defer fout.Close()
	_, err = fout.Write(data)
	if err != nil {
		fmt.Println(err)
		return err
	}
	return nil
}

func MIPSRun(basedir string, target int, nodeID int, programPath string, inputPath string, outputGolden bool, outputMode int, nodeCount int) {
	regfault := -1
	regfault_str, regfault_valid := os.LookupEnv("REGFAULT")
	if regfault_valid {
		regfault, _ = strconv.Atoi(regfault_str)
	}

	// step 1, generate the checkpoints every million steps using unicorn
	ram := make(map[uint32](uint32))

	lastStep := 1
	reachFinalState := true // if the target >= total step, the targt will not be saved

	mu := GetHookedUnicorn(basedir, ram, func(step int, mu uc.Unicorn, ram map[uint32](uint32)) {
		if step == regfault {
			fmt.Printf("regfault at step %d\n", step)
			mu.RegWrite(uc.MIPS_REG_V0, 0xbabababa)
		}
		if step == target {

			timer.StopTimer("uc-exec")

			reachFinalState = false
			SyncRegs(mu, ram)
			fn := fmt.Sprintf("%s/checkpoint_%d_%d.json", basedir, nodeID, step)
			WriteCheckpointWithNodeID(ram, fn, step, nodeID, nodeCount, outputMode)
			if step == target {
				// done
				mu.RegWrite(uc.MIPS_REG_PC, 0x5ead0004)
			}
		}
		lastStep = step + 1
	})

	ZeroRegisters(ram)
	// not ready for golden yet
	LoadMappedFileUnicorn(mu, programPath, ram, 0)
	// load input
	if inputPath != "" {
		LoadInputData(mu, inputPath, ram)
	}

	if outputGolden {
		WriteCheckpointWithNodeID(ram, fmt.Sprintf("%s/%d_golden.json", basedir, nodeID), -1, nodeID, nodeCount, outputMode)
		fmt.Println("Writing golden snapshot and exiting early without execution")
		return
	}

	// do not need if we just run pure computation task
	// LoadMappedFileUnicorn(mu, fmt.Sprintf("%s/input", basedir), ram, 0x30000000)

	timer.StartTimer("uc-exec")
	mu.Start(0, 0x5ead0004)
	timer.StopTimer("uc-exec")

	if reachFinalState {
		fmt.Printf("reach the final state, total step: %d, target: %d\n", lastStep, target)
		WriteCheckpointWithNodeID(ram, fmt.Sprintf("%s/checkpoint_%d_%d.json", basedir, nodeID, lastStep), lastStep, nodeID, nodeCount, outputMode)
	}

	if target == -1 {

		fmt.Println("lastStep: ", lastStep)
		WriteCheckpointWithNodeID(ram, fmt.Sprintf("%s/checkpoint_%d_final.json", basedir, nodeID), lastStep, nodeID, nodeCount, outputMode)

	}
}

func MIPSRunCompatible(basedir string, target int, programPath string, modelPath string, inputPath string, outputGolden bool, outputMode int) {
	regfault := -1
	regfault_str, regfault_valid := os.LookupEnv("REGFAULT")
	if regfault_valid {
		regfault, _ = strconv.Atoi(regfault_str)
	}

	// step 1, generate the checkpoints every million steps using unicorn
	ram := make(map[uint32](uint32))

	lastStep := 1
	reachFinalState := true // if the target >= total step, the targt will not be saved

	mu := GetHookedUnicorn(basedir, ram, func(step int, mu uc.Unicorn, ram map[uint32](uint32)) {
		if step == regfault {
			fmt.Printf("regfault at step %d\n", step)
			mu.RegWrite(uc.MIPS_REG_V0, 0xbabababa)
		}
		if step == target {
			reachFinalState = false
			SyncRegs(mu, ram)
			fn := fmt.Sprintf("%s/checkpoint_%d.json", basedir, step)
			WriteCheckpoint(ram, fn, step, 0)
			if step == target {
				// done
				mu.RegWrite(uc.MIPS_REG_PC, 0x5ead0004)
			}
		}
		lastStep = step + 1
	})

	ZeroRegisters(ram)
	// not ready for golden yet
	LoadMappedFileUnicorn(mu, programPath, ram, 0)
	// load input
	if inputPath != "" {
		LoadInputData(mu, inputPath, ram)
	}
	LoadModel(mu, modelPath, ram)

	if outputGolden {
		WriteCheckpoint(ram, fmt.Sprintf("%s/golden.json", basedir), -1, 0)
		fmt.Println("Writing golden snapshot and exiting early without execution")
		return
	}

	// do not need if we just run pure computation task
	// LoadMappedFileUnicorn(mu, fmt.Sprintf("%s/input", basedir), ram, 0x30000000)

	SyncRegs(mu, ram)
	mu.Start(0, 0x5ead0004)
	SyncRegs(mu, ram)

	if reachFinalState {
		fmt.Printf("reach the final state, total step: %d, target: %d\n", lastStep, target)
		WriteCheckpoint(ram, fmt.Sprintf("%s/checkpoint_%d.json", basedir, lastStep), lastStep, 0)
	}

	if target == -1 {

		fmt.Println("lastStep: ", lastStep)
		WriteCheckpoint(ram, fmt.Sprintf("%s/checkpoint_final.json", basedir), lastStep, 0)
		fmt.Printf("PC: %x\n", ram[0xC0000080])
	}
}
