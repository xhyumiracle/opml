package vm

import (
	"fmt"
	"io/ioutil"

	llama "mlgo/examples/llama/llama_go"
	"mlgo/examples/mnist"
	"mlgo/ml"

	"mlvm/timer"
)

func GenGraphData(modelName string, nodeID int, modelFile string, prompt string, dataFile string) ([]byte, int, error) {
	graph, mlctx, _ := GenGraph(modelName, nodeID, modelFile, prompt, dataFile)
	envBytes, nodeCount, err := graphDataByNode(graph, mlctx, nodeID)
	return envBytes, nodeCount, err
}

func graphDataByNode(graph *ml.Graph, mlctx *ml.Context, nodeID int) ([]byte, int, error) {

	timer.StartTimer("graph-compute")

	ml.GraphComputeByNodes(mlctx, graph, nodeID)

	timer.StopTimer("graph-compute")

	timer.StartTimer("graph-node2bytes")

	envBytes := ml.SaveComputeNodeEnvToBytes(uint32(nodeID), graph.Nodes[nodeID], graph, true)

	timer.StopTimer("graph-node2bytes")

	return envBytes, int(graph.NodesCount), nil
}

func GenGraph(modelName string, nodeID int, modelFile string, prompt string, dataFile string) (*ml.Graph, *ml.Context, error) {
	var graph *ml.Graph
	var mlctx *ml.Context
	var err error

	if modelName == "MNIST" {
		fmt.Println("in GenGraphData, ******* params.InputPath ****************", dataFile)
		graph, mlctx, err = MNISTGraph(nodeID, modelFile, dataFile)
	} else { // if modelName == "LLAMA"
		graph, mlctx, err = LLAMAGraph(nodeID, modelFile, prompt)
	}
	return graph, mlctx, err
}

func LLAMAGraph(nodeID int, modelFile string, prompt string) (*ml.Graph, *ml.Context, error) {
	if modelFile == "" {
		modelFile = "./mlgo/examples/llama/models/llama-7b-fp32.bin"
	}
	if prompt == "" {
		prompt = "How to combine AI and blockchain?"
	}

	threadCount := 32

	timer.StartTimer("readmodel")

	ctx, err := llama.LoadModel(modelFile, true)
	fmt.Println("Load Model Finish")
	if err != nil {
		fmt.Println("load model error: ", err)
		return nil, nil, err
	}

	timer.StopTimer("readmodel")

	embd := ml.Tokenize(ctx.Vocab, prompt, true)
	return llama.ExpandGraph(ctx, embd, uint32(len(embd)), 0, threadCount)
}

func MNISTGraph(nodeID int, modelFile string, dataFile string) (*ml.Graph, *ml.Context, error) {
	threadCount := 1
	if modelFile == "" {
		modelFile = "../../mlgo/examples/mnist/models/mnist/ggml-model-small-f32.bin"
	}
	if dataFile == "" {
		dataFile = "../../mlgo/examples/mnist/models/mnist/input_7"
	}

	timer.StartTimer("readmodel")

	model, err := mnist.LoadModel(modelFile)
	if err != nil {
		fmt.Println("Load model error: ", err)
		return nil, nil, err
	}

	timer.StopTimer("readmodel")

	// load input
	input, err := MNIST_Input(dataFile, false)
	if err != nil {
		fmt.Println("Load input data error: ", err)
		return nil, nil, err
	}
	return mnist.ExpandGraph(model, threadCount, input)
}

func MNIST_Input(dataFile string, show bool) ([]float32, error) {
	buf, err := ioutil.ReadFile(dataFile)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}
	digits := make([]float32, 784)

	// render the digit in ASCII
	var c string
	for row := 0; row < 28; row++ {
		for col := 0; col < 28; col++ {
			digits[row*28+col] = float32(buf[row*28+col])
			if buf[row*28+col] > 230 {
				c += "*"
			} else {
				c += "_"
			}
		}
		c += "\n"
	}
	if show {
		fmt.Println(c)
	}

	return digits, nil
}

// for compatible, cam rm
func LLAMA(nodeID int, modelFile string, prompt string) ([]byte, int, error) {
	graph, mlctx, err := LLAMAGraph(nodeID, modelFile, prompt)
	if err != nil {
		fmt.Println("LLAMAGraph error: ", err)
		return nil, 0, err
	}
	return graphDataByNode(graph, mlctx, nodeID)
}

// for compatible, cam rm
func MNIST(nodeID int, modelFile string, dataFile string) ([]byte, int, error) {
	graph, mlctx, err := MNISTGraph(nodeID, modelFile, dataFile)
	if err != nil {
		fmt.Println("MNISTGraph error: ", err)
		return nil, 0, err
	}
	return graphDataByNode(graph, mlctx, nodeID)
}

func PrintGraph(graph *ml.Graph, modelName string) {
	ml.PrintGraph(graph, modelName)
}
