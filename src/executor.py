from abc import abstractmethod
from typing import IO
from .clparser import CmdIR
import io
import os
import sys
import subprocess


class CmdExecutor(object):
    """
    An abstract class for a command execution

    Args:
        cmd (CmdIR): the command which need to be executed

    Attributes:
        name (str): the command name
        args (list): the command args

    Raises:
        RuntimeError: if there is some error

        FileNotFoundError: for `cat` and `wc` command only,
            if no such file in directory

    """

    def __init__(self, cmd: CmdIR) -> None:
        self.name = cmd.name
        self.args = cmd.args

    @abstractmethod
    def execute(self, istream: io.StringIO) -> io.StringIO:
        """
        Execute the command

        Args:
            istream (io.StringIO): input stream

        Returns:
            io.StringIO: output stream with the result of execution

        """

        pass

    @classmethod
    @abstractmethod
    def _cmdImpl(cls, istream: IO) -> io.StringIO:
        """
        The implementation of the concrete command

        """

        pass

    @classmethod
    def _readFromStream(cls, istream: io.StringIO) -> io.StringIO:
        newStream = io.StringIO(istream.getvalue())
        return cls._cmdImpl(newStream)

    @classmethod
    def _readFromConsole(cls) -> io.StringIO:
        return cls._cmdImpl(sys.stdin)

    @classmethod
    def _readFromFile(cls, filename: str) -> io.StringIO:
        with open(filename, 'r') as f:
            return cls._cmdImpl(f)


class EchoExecutor(CmdExecutor):
    """
    `echo`: print given arguments

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()

        try:
            ostream.write(' '.join(self.args))
        except Exception:
            raise RuntimeError('echo: check your arguments')

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

        try:
            ostream.write(os.getcwd())
        except Exception:
            raise RuntimeError('pwd: some bads with pwd')

        return ostream


class CatExecutor(CmdExecutor):
    """
    `cat [FILE]`: print the FILE content
        if there is no FILE, cat prints
        the content of the input stream

    can be used only with one file

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    @classmethod
    def _cmdImpl(cls, istream: IO) -> io.StringIO:
        ostream: io.StringIO = io.StringIO()

        for line in istream:
            ostream.write(line)

        return ostream

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        cntArgs: int = len(self.args)

        if cntArgs == 1:
            filename: str = self.args[0]
            ostream = self._readFromFile(filename)
        elif cntArgs == 0:
            if istream.getvalue():
                ostream = self._readFromStream(istream)
            else:
                ostream = self._readFromConsole()
        else:
            raise ValueError(
                f'cat: cat supports only one file, but given {cntArgs}')

        return ostream


class WcExecutor(CmdExecutor):
    """
    `wc FILE`: print a count of line,
    count of word, count of char in the FILE
    or the input stream, if there is no FILE

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    @classmethod
    def _cmdImpl(cls, istream: IO) -> io.StringIO:
        ostream: io.StringIO = io.StringIO()

        lineCnt, wordCnt, charCnt = 0, 0, 0

        for line in istream:
            lineCnt += 1
            wordCnt += len(line.split())
            charCnt += len(line)

        ostream.write(f'{lineCnt} {wordCnt} {charCnt}')

        return ostream

    @classmethod
    def _readFromFile(cls, filename: str) -> io.StringIO:
        ostream = super()._readFromFile(filename)
        ostream.write(f' {filename}')
        return ostream

    @classmethod
    def _readFromStream(cls, istream: io.StringIO) -> io.StringIO:
        text = istream.getvalue()
        hasEndlInEnd: bool = (text[-1] == '\n')

        if not hasEndlInEnd:
            text = text + '\n'

        newStream = io.StringIO(text)
        return WcExecutor._cmdImpl(newStream)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        cntArgs: int = len(self.args)
        filename: str = ''

        if cntArgs == 1:
            filename = self.args[0]
            ostream = WcExecutor._readFromFile(filename)
        elif cntArgs == 0:
            if istream.getvalue():
                ostream = WcExecutor._readFromStream(istream)
            else:
                ostream = WcExecutor._readFromConsole()
        else:
            raise ValueError(
                f'wc: wc supports only one file, but given {cntArgs}')

        return ostream


class ExitExecutor(CmdExecutor):
    """
    Stops the session

    """

    def execute(self, istream: io.StringIO) -> io.StringIO:
        raise EOFError


class ExternalExecutor(CmdExecutor):
    """
    Run some external process

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()

        externalProcess = subprocess.Popen([self.name, *self.args],
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

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

    if name == 'exit':
        return ExitExecutor(cmd)

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
        try:
            result = cmd.execute(result)
        except Exception as e:
            raise e

    result.write('\n')

    return result
