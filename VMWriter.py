from symbolTable import SymbolTable
class VMWriter:
    def __init__(self, output_file):
        """
                Initializes a new output .vm file/stream and prepares it for writing.
                :param out_file: The name of the output file or stream
                """
        self.output_file = open(output_file, "w")

    def writer(self, command):
        self.output_file.write(command + "\n")

    def close(self):
        self.output_file.close()

    def writePush(self, segment, index):
        self.output_file.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        self.output_file.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command):
        self.output_file.write(f"{command}\n")

    def writeLabel(self, label):
        LABEL = label.upper()
        self.output_file.write(f"({LABEL})\n")

    def writeGoto(self, label):
        self.output_file.write(f"goto {label}\n")

    def writeIf(self, label):
        self.output_file.write(f"if-goto {label}\n")

    def writeCall(self, name, nArgs):
        self.output_file.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name, nLocals):
        self.output_file.write(f"function {name} {nLocals}\n")

    def writeReturn(self):
        self.output_file.write("return\n")









