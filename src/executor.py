from .clparser import CmdIR
import io
import os

# TODO
# stream = io.StringIO() <=> stream.truncate(0); stream.seek(0)


class CmdExecutor(object):
    """
    An abstract class for a command execution

    Args:
        cmd (CmdIR): the command which need to be executed

    Attributes:
        name (str): the command name 
        args (list): the command args

    TODO: rewrite with `return code` and get in-out streams

    """

    def __init__(self, cmd: CmdIR) -> None:
        self.name = cmd.name
        self.args = cmd.args

    def execute(self, stream: io.StringIO) -> io.StringIO:
        """
        Execute the command

        Args:
            stream (io.StringIO): input stream

        Returns:
            io.StringIO: output stream with the result of execution

        """

        pass


class EchoExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()

        argsStr = ''.join(self.args)
        stream.write(argsStr)
        return stream


class PwdExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()
        stream.write(os.getcwd())
        return stream


class CatExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()
        filename: str = self.args[0]
        with open(filename) as f:
            stream.write(f.read())

        return stream


class WcExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()
        filename: str = self.args[0]

        lineCnt, wordCnt, charCnt = 0, 0, 0

        with open(filename) as f:
            for line in f:
                lineCnt += 1
                wordCnt += len(line.split())
                charCnt += len(line)

        stream.write(f'{lineCnt} {wordCnt} {charCnt} {filename}')
        return stream


def processCmd(cmd: CmdIR) -> CmdExecutor:
    """
    Map the command to its executor 

    Args:
        cmd (CmdIR): the command

    Returns:
        CmdExecutor: the executor for the command

    Raises:
        TODO: add more exceptions
        NotImplemetedError

    """

    name: str = cmd.name

    if name == 'echo':
        return EchoExecutor(cmd)

    if name == 'pwd':
        return PwdExecutor(cmd)

    if name == 'cat':
        return CatExecutor(cmd)

    if name == 'wc':
        return WcExecutor(cmd)

    # TODO: unknown command
    print('Unknown command')
    raise NotImplementedError


def runCommand(cmds: list[CmdIR]) -> io.StringIO:
    """
    Execute the command

    Args:
        cmds (list[CmdIR]): commands

    Returns:
        io.StringIO: the output stream with the result of the command 

    """

    result = io.StringIO()
    cmdsExec: list[CmdExecutor] = list(map(processCmd, cmds))

    for cmd in cmdsExec:
        result = cmd.execute(result)

    result.write('\n')

    return result
