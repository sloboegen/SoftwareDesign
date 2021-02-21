from io import StringIO
from .executor import runCommand
from .expansion import expansion
from .clparser import parseDecl, parsePipes, checkDecl, VarDecl


class Session():
    def __init__(self) -> None:
        self.state = dict()

    def getCmdResult(self, line: str) -> StringIO:
        if checkDecl(line):
            varDecl = parseDecl(line)
            self.__updateState(varDecl)

            return StringIO('')

        cmds = parsePipes(line)
        cmds = list(map(lambda c: expansion(c, self.state), cmds))
        ostr = runCommand(cmds)

        return ostr

    def work(self) -> bool:
        print('> ', end='')

        line: str = input()

        if line == '':
            return True

        if line == 'exit':
            return False

        ostr = self.getCmdResult(line)

        print(ostr.getvalue(), end='')

        ostr.close()

        self.endSession()

        return True

    def __updateState(self, decl: VarDecl):
        self.state[decl.var] = decl.value

    def endSession(self) -> None:
        self.state.clear()