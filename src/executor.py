from clparser import CmdIR
import io

# TODO
# stream = io.StringIO() <=> stream.truncate(0); stream.seek(0)


class CmdExecutor(object):
    def __init__(self, cmd: CmdIR) -> None:
        self.name = cmd.name
        self.args = cmd.args

    def execute(self, stream: io.StringIO) -> io.StringIO:
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
        stream.write('This is output of pwd')
        return stream


class CatExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()
        filename: str = self.args
        with open(filename) as f:
            stream.write(f.read())

        return stream


class WcExecutor(CmdExecutor):
    def __init__(self, cmd: CmdIR) -> None:
        super().__init__(cmd)

    def execute(self, stream: io.StringIO) -> io.StringIO:
        stream = io.StringIO()
        filename: str = self.args

        lineCnt, wordCnt, charCnt = 0, 0, 0

        with open(filename) as f:
            for line in f:
                lineCnt += 1
                wordCnt += len(line.split())
                charCnt += len(line)
        
        stream.write(f'{lineCnt} {wordCnt} {charCnt} {filename}')
        return stream



def processCmd(cmd: CmdIR) -> CmdExecutor:
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
    result = io.StringIO()
    cmdsExec: list[CmdExecutor] = list(map(processCmd, cmds))

    for cmd in cmdsExec:
        result = cmd.execute(result)

    return result
