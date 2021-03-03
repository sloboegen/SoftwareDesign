from __future__ import annotations
import re


class CmdIR:
    """
    Contains an intermediate representation of a command

    Args:
        cmd (str): the user entered command

    Attributes:
        name (str): the command name
        args (list[str]): the command args splited by whitespace

    """

    def __init__(self, cmd: str) -> None:
        self.name: str
        self.args: list[str]

        self.name, *self.args = cmd.split()

    def __str__(self) -> str:
        return f'{self.name} {" ".join(self.args)}'

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, CmdIR):
            return False

        return self.name == o.name and self.args == o.args


class VarDecl:
    """
    Contains an intermediate representation
    of a variable declaration and methods
    for working with it

    Args:
        decl (str): the user entered decalration

    Attributes:
        var (str): the variable name
        value (str): the value of this variable

    """

    declRe = re.compile(r'[A-Za-z]\w*=([^|<>\'"]*|\'.*\'|\".*\")$')

    def __init__(self, decl: str) -> None:
        self.var: str
        self.value: str

        decl = decl.strip()
        splitPos = decl.find('=')
        self.var = decl[:splitPos]
        self.value = self.__parseQuotes(decl[splitPos + 1:])

    def __str__(self) -> str:
        return f'{self.var}={self.value}'

    @staticmethod
    def checkDecl(line: str) -> bool:
        """
        Check statement is variable decalartion

        Args:
            line (str): the user entered line

        Returns:
            bool: True if line is variable declaration, False otherwise

        """

        return bool(VarDecl.declRe.match(line))

    @staticmethod
    def parseDecl(line: str) -> VarDecl:
        """
        Wrapper for `VarDecl` constructor
        """
        return VarDecl(line)

    def __parseQuotes(self, value: str) -> str:
        if not value:
            return value

        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]

        if value[0] == "'" and value[-1] == "'":
            return value[1:-1]

        return value


def parsePipes(line: str) -> list[str]:
    """
    Split the command with a pipe

    Args:
        line (str): the user entered line

    Returns:
        list[str]: the list of all commands between pipes

    """

    # cmds: list[str] = line.split('|')
    # cmdsIR: list[CmdIR] = [CmdIR(cmd) for cmd in cmds]
    # return cmdsIR

    splited: list[str] = []
    curCmd: str = ''
    inSingleQuote: bool = False
    inDoubleQuote: bool = False

    # print(line)

    for sym in line:
        if sym == '"':
            inDoubleQuote ^= True
            curCmd += sym
            continue

        if sym == "'":
            inSingleQuote ^= True
            curCmd += sym
            continue

        if sym != '|':
            curCmd += sym
            continue

        if (sym == '|') and (inSingleQuote or inDoubleQuote):
            curCmd += sym
            continue

        splited.append(curCmd.strip())
        curCmd = ''

    if curCmd != '':
        splited.append(curCmd.strip())
        curCmd = ''

    return splited

    # print(splited)

    # return [CmdIR(c) for c in splited]
