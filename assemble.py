# run with: python3 assemble.py <file with list of assembly instructions>
# try it with the provided insns file: python3 assemble.py insns

import subprocess
import sys
import os
from collections import namedtuple

if len( sys.argv ) == 2:
    filename = sys.argv[1]
else:
    print("Need to pass a file")
    print("Usage: python3 assemble.py <file with a list of RISCV assembly instructions>")
    exit(0)

SubprocessResult = namedtuple('SubprocessResult', ['returncode', 'stdout', 'stderr'])
TIMEOUT_SIGNAL = -1

def run(*args, **kwargs):
    try:
        p = subprocess.run(*args, preexec_fn=os.setsid, **kwargs)
        code = p.returncode
        output = p.stdout
        error = p.stderr
    except subprocess.TimeoutExpired as e:
        timeout_str = "Timeout ({}s) expired!".format(e.timeout)
        code = TIMEOUT_SIGNAL
        output = timeout_str
        error = timeout_str
    return SubprocessResult(returncode=code, stdout=output, stderr=error)

# get initial instructions
input_insns = []
with open(filename, "rb") as f:
    for line in f:
        line = line.decode('utf8').strip()
        if not (len(line) == 0 or line.startswith("#")):
            input_insns.append(line)

compile_cmd = "riscv32-unknown-linux-gnu-gcc"
compile_flags = ["-march=rv32i","-mabi=ilp32"]
compile_tmp = ["-c", "tmp.S", "-o", "tmp.o"]

objcopy_cmd = "riscv32-unknown-linux-gnu-objcopy"
objcopy_flags = ["-O", "binary", "-j", ".text"]
objcopy_tmp = ["tmp.o", "tmp.bin"]

# move the instructions to a .S file
run(["cp", filename , "tmp.S"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# compile the .S file to a .o file
result = run([ compile_cmd ] + compile_flags + compile_tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
if result.returncode != 0:
    print(result.stdout.decode('utf-8', errors='ignore'))
    print("There was an error compiling your RISCV assembly. Make sure that it is valid RISCV assembly.")
    exit(0)

# extract the .text section for the object file into a raw binary file
result = run([ objcopy_cmd ] + objcopy_flags + objcopy_tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
if result.returncode != 0:
    print(result.stdout.decode('utf-8', errors='ignore'))
    print("The assembler ran into encountered an error. Check the output for more information.")
    exit(0)

# read the raw binary file word by word
bin_output = []
with open("tmp.bin", "rb") as f:
    word = f.read(4)
    while word != b"":
        # reverse the bytes to preserve endianess
        word = word[::-1]
        bin_output.append(word.hex())
        word = f.read(4)

# clean up tmp files
run(["rm", "tmp.S", "tmp.o", "tmp.bin"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# output hex of instructions
with open(filename+".hex", "w+") as f:
    f.write("\n".join(bin_output) + "\n")

# output annotated hex of instructions
joined = [b +" #\t" + i for (b,i) in zip(bin_output, input_insns)]
with open(filename+".ahex", "w+") as f:
    f.write("\n".join(joined) + "\n")
