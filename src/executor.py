from .clparser import CmdIR
import io
import os
import subprocess


class CmdExecutor(object):
    """
    An abstract class for a command execution

    Args:
        cmd (CmdIR): the command which need to be executed

    Attributes:
        name (str): the command name
        args (list): the command args

    """

    def __init__(self, cmd: CmdIR) -> None:
        self.name = cmd.name
        self.args = cmd.args

    def execute(self, istream: io.StringIO) -> io.StringIO:
        """
        Execute the command

        Args:
            istream (io.StringIO): input stream

        Returns:
            io.StringIO: output stream with the result of execution

        """

        pass


class EchoExecutor(CmdExecutor):
    """
    `echo`: print given arguments

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        ostream.write(self.args)
        return ostream


class PwdExecutor(CmdExecutor):
    """
    `pwd`: print current directory
    args isn't required

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        ostream.write(os.getcwd())
        return ostream


class CatExecutor(CmdExecutor):
    """
    `cat FILE`: print the FILE content
    can be used only with one file

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        assert len(self.args.split()) == 1, "Only one file"
        filename: str = self.args
        with open(filename) as f:
            ostream.write(f.read())

        return ostream


class WcExecutor(CmdExecutor):
    """
    `wc FILE`: print a count of line,
    count of word, count of char in the FILE

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()

        assert len(self.args.split()) == 1, "Only one file"

        filename: str = self.args

        lineCnt, wordCnt, charCnt = 0, 0, 0

        with open(filename) as f:
            for line in f:
                lineCnt += 1
                wordCnt += len(line.split())
                charCnt += len(line)

        ostream.write(f'{lineCnt} {wordCnt} {charCnt} {filename}')
        return ostream


class ExternalExecutor(CmdExecutor):
    """
    Run some external process

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()

        externalProcess = subprocess.Popen([self.name, self.args],
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE)

        encodedInput = bytes(istream.getvalue().encode('utf-8'))

        externalProcess.stdin.write(encodedInput)
        result = externalProcess.communicate()[0].decode('utf-8')
        externalProcess.stdin.close()

        ostream.write(result)

        return ostream


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

    return ExternalExecutor(cmd)


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
