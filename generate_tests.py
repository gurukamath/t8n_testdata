import json
import os
import shutil
import subprocess
from copy import deepcopy
from typing import Any

geth_evm_path = "../go-ethereum/build/bin/evm"

base_dir = "."

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

extra_params_dict = {5: ["--state.reward", "128"]}


def get_args(testdata: int, fork: str, extra_params: Any = None) -> Any:

    if extra_params is None:
        extra_params = []

    args = [
        "t8n",
        "--input.alloc",
        f"__BASEDIR__/fixtures/testdata/{testdata}/alloc.json",
        "--input.env",
        f"__BASEDIR__/fixtures/testdata/{testdata}/env.json",
        "--input.txs",
        f"__BASEDIR__/fixtures/testdata/{testdata}/txs.json",
    ]

    args += ["--state.fork", fork] + extra_params

    return args


def get_testdata() -> Any:
    test_dirs = [
        f.path
        for f in os.scandir(os.path.join(base_dir, "fixtures", "testdata"))
        if f.is_dir()
    ]
    testdata = []
    for test_dir in test_dirs:
        try:
            testdata.append(int(test_dir.split("/")[-1]))
        except ValueError:
            continue

    return testdata


def main() -> None:

    expected_path = os.path.join("fixtures", "expected")
    commands_path = "commands.json"

    if os.path.exists(commands_path):
        os.remove(commands_path)

    if os.path.exists(expected_path):
        shutil.rmtree(expected_path)

    os.mkdir(expected_path)

    cmds = {}
    for testdata in get_testdata():
        for fork in forks:

            parameters = {}

            output_dir = os.path.join(expected_path, str(testdata))
            output_file = os.path.join(output_dir, f"{fork}.json")
            output_file_alloc = os.path.join(output_dir, f"{fork}_alloc.json")
            output_file_result = os.path.join(
                output_dir, f"{fork}_result.json"
            )

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if testdata in extra_params_dict:
                extra_params = extra_params_dict[testdata]
            else:
                extra_params = None

            args = get_args(testdata, fork, extra_params)
            parameters["args"] = args
            subprocess_args = [geth_evm_path]
            for arg in args:
                if "__BASEDIR__" in arg:
                    subprocess_args.append(
                        arg.replace("__BASEDIR__", base_dir)
                    )
                else:
                    subprocess_args.append(arg)

            subprocess_args += [
                "--output.alloc",
                output_file_alloc,
                "--output.result",
                output_file_result,
            ]

            # Run subprocess hide the output and capture only the error
            subproc_run = subprocess.run(
                subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            if subproc_run.returncode:
                print(testdata, fork, subproc_run.stderr.decode("utf-8"))
                parameters["success"] = False
                cmds[output_file] = deepcopy(parameters)
                continue

            parameters["success"] = True
            cmds[output_file] = deepcopy(parameters)

            with open(output_file_alloc, "r") as f:
                alloc = json.load(f)

            with open(output_file_result, "r") as f:
                result = json.load(f)

            output = {}
            output["alloc"] = alloc
            output["result"] = result

            with open(output_file, "w") as f:
                json.dump(output, f, indent=4)

            os.remove(output_file_alloc)
            os.remove(output_file_result)

    with open(commands_path, "w") as f:
        json.dump(cmds, f, indent=4)


if __name__ == "__main__":
    main()
