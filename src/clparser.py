from __future__ import annotations
import re


class CmdIR:
    """
    Contains an intermediate representation of a command

    Args:
        cmd (str): the user entered command

    Attributes:
        name (str): the command name
        args (str): the command args splited by whitespace

    """

    def __init__(self, cmd: str) -> None:
        self.name: str
        self.args: str

        splitted = cmd.split()

        # TODO: check empty
        self.name = splitted[0]
        self.args = ' '.join(splitted[1:])

    def __str__(self) -> str:
        return f'{self.name} {self.args}'


class VarDecl:
    """
    Contains an intermediate representation
    of a variable declaration and methods
    for working with it

    Args:
        decl (str): the user entered decalration

    Attributes:
        var (str): the variable name
        value (list[str]): the value of this variable

    """

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

        TODO:
            Fix re-checker. Value in quotes are unmatched now

        """

        declRe = re.compile(r'[A-Za-z]\w*=(.+|\'.*\'|\".*\")$')
        return bool(declRe.match(line))

    @staticmethod
    def parseDecl(line: str) -> VarDecl:
        """
        Wrapper for `VarDecl` constructor
        """
        return VarDecl(line)

    def __parseQuotes(self, value: str) -> str:
        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]

        if value[0] == "'" and value[-1] == "'":
            return value[1:-1]

        return value


def parsePipes(line: str) -> list[CmdIR]:
    """
    Split the command with a pipe

    Args:
        line (str): the user entered line

    Returns:
        list[CmdIR]: the list of all commands between pipes

    """

    cmds: list[str] = line.split('|')
    cmdsIR: list[CmdIR] = [CmdIR(cmd) for cmd in cmds]

    return cmdsIR
