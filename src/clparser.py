import re


class CmdIR:
    def __init__(self, cmd: str) -> None:
        self.name: str
        self.args: list[str]

        splitted = cmd.split()

        # TODO: check empty
        self.name = splitted[0]
        self.args = ' '.join(splitted[1:])

    def __str__(self) -> str:
        return f'name: {self.name}; args: {self.args}'


class VarDecl:
    def __init__(self, decl: str) -> None:
        self.var: str
        self.value: str

        var, value = decl.split('=')
        self.var = var.strip()
        self.value = value.strip()


def checkDecl(line: str) -> bool:
    # declRe = re.compile('[A-Za-z][A-Za-z0-9]+=[A-Za-z0-9]+$')
    return '=' in line


def parseDecl(line: str) -> VarDecl:
    return VarDecl(line)


def parsePipes(line: str) -> list[CmdIR]:
    cmds: list[str] = line.split('|')
    cmdsIR: list[CmdIR] = [CmdIR(cmd) for cmd in cmds]

    return cmdsIR
