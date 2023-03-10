import os
import json
import subprocess

geth_evm_path = "/Users/guruprasad/Documents/Programming/Ethereum/go-ethereum/build/bin/evm"

output_base_dir = "/Users/guruprasad/Documents/Programming/Ethereum/execution-specs/.vscode/evm_tools_generated_testdata"

forks = [
    "Frontier",
    "Homestead",
    "EIP150",
    "EIP158",
    "Byzantium",
    "Constantinople",
    "Istanbul",
    "MuirGlacier",
    "Berlin",
    "London",
    "ArrowGlacier",
    "GrayGlacier",
]


def get_args(testdata, fork, extra_params=None):

    if extra_params is None:
        extra_params = []

    args = [
        "t8n",
        "--input.alloc",
        f".vscode/evm_tools_generated_testdata/{testdata}/alloc.json",
        "--input.env",
        f".vscode/evm_tools_generated_testdata/{testdata}/env.json",
        "--input.txs",
        f".vscode/evm_tools_generated_testdata/{testdata}/txs.json",
    ]

    args += ["--state.fork", fork] + extra_params

    return args


def get_testdata():
    test_dirs = [f.path for f in os.scandir(output_base_dir) if f.is_dir()]
    testdata = []
    for test_dir in test_dirs:
        try:
            testdata.append(int(test_dir.split("/")[-1]))
        except ValueError:
            continue

    return testdata



def main():

    for testdata in get_testdata():
        for fork in forks:

            output_dir = os.path.join(output_base_dir, "expected", str(testdata))
            output_file = os.path.join(output_dir, f"{fork}.json")
            output_file_alloc = os.path.join(output_dir, f"{fork}_alloc.json")
            output_file_result = os.path.join(output_dir, f"{fork}_result.json")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            args = get_args(testdata, fork)
            subprocess_args = [geth_evm_path] + args + ["--output.alloc", output_file_alloc, "--output.result", output_file_result]

            # Run subprocess hide the output and capture only the error
            subproc_run = subprocess.run(subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if subproc_run.returncode:
                print(testdata, fork, subproc_run.stderr.decode("utf-8"))
                continue

            with open(output_file_alloc, "r") as f:
                alloc = json.load(f)

            with open(output_file_result, "r") as f:
                result = json.load(f)

            output = {}
            output["alloc"] = alloc
            output["result"] = result
            output["args"] = args
            output["expected"] = output_file

            with open(output_file, "w") as f:
                json.dump(output, f, indent=4)


            os.remove(output_file_alloc)
            os.remove(output_file_result)


if __name__ == "__main__":
    main()

