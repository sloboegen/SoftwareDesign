from abc import abstractmethod
from typing import IO
from .clparser import CmdIR
import io
import os
import sys
import subprocess
import re


class CmdExecutor(object):
    """
    An abstract class for a command execution

    Args:
        cmd (CmdIR): the command which need to be executed

    Attributes:
        name (str): the command name
        args (list): the command args
        keys (list[str, str]): the command keys

    Raises:
        RuntimeError: if there is some error

        FileNotFoundError: for `cat` and `wc` command only,
            if no such file in directory

    """

    def __init__(self, cmd: CmdIR) -> None:
        self.name = cmd.name
        self.args = cmd.args
        self.keys = cmd.keys

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
    def _cmdImpl(cls, istream: IO, *args) -> io.StringIO:
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


class GrepExecutor(CmdExecutor):
    """
    `grep pattern FILE`
    `... | grep pattern`: prints all lines where pattern in

    Attributes:
        iKey (bool): is it need to match with case insensitive
        wKey (bool): is it need to match a whole word
        aKey (int): the count of strings need to print after match

    """

    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

        # -i: case insensitive
        self.iKey: bool = '-i' in cmd.keys

        # -w: match all word
        self.wKey: bool = '-w' in cmd.keys

        # -A n: print n lines after match
        self.aKey = int(cmd.keys['-A']) if '-A' in cmd.keys else 0

    def _matchLine(self, line: str, pattern: str) -> bool:
        modified = line

        if self.iKey:
            pattern = pattern.lower()
            modified = modified.lower()

        if self.wKey:
            pattern = rf'\b{pattern}\b'

        regex = re.compile(rf'{pattern}')

        return bool(regex.search(modified))

    def _getFileLines(self, filename: str) -> list[str]:
        result = []

        try:
            with open(filename, 'r') as f:
                result = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f'grep: {filename}: no such file')

        return result

    def _getStreamLines(self, istream: io.StringIO) -> list[str]:
        splited = istream.getvalue().split('\n')
        return [s + '\n' for s in splited]

    def execute(self, istream: io.StringIO) -> io.StringIO:
        ostream = io.StringIO()
        splitted: list[str] = self.args
        pattern: str = splitted[0]

        realInput: list[str] = []

        if len(splitted) == 2:
            filename: str = splitted[1]
            realInput = self._getFileLines(filename)
        else:
            realInput = self._getStreamLines(istream)

        result: str = ''
        fstMatch = False

        for num, line in enumerate(realInput):
            if self._matchLine(line, pattern):
                if self.aKey != 0 and fstMatch:
                    result += '--\n'
                fstMatch = True
                finish = min(len(realInput), num + self.aKey)
                result += ''.join(realInput[num: finish + 1])

        ostream.write(result)

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

    if name == 'grep':
        return GrepExecutor(cmd)

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
