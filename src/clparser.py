from __future__ import annotations
import re


class CmdIR:
    """
    Contains an intermediate representation of a command

    Args:
        cmd (str): the user entered command

    Attributes:
        name (str): the command name
        args (list[str]): the command args

    """

    def __init__(self, cmd: str) -> None:
        self.name: str
        self.args: list[str]

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

        # TODO: fix splitting
        var, value = decl.split('=')
        self.var = var.strip()
        self.value = value.strip()

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

        declRe = re.compile(r'[A-Za-z]\w*=\w+$')
        return bool(declRe.match(line))

    @staticmethod
    def parseDecl(line: str) -> VarDecl:
        """
        Wrapper for `VarDecl` constructor
        """
        return VarDecl(line)


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
