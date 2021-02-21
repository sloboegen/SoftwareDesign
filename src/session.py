import clparser
from executor import runCommand
from expansion import expansion


class Session():
    def __init__(self) -> None:
        self.state = dict()

    def work(self) -> bool:
        print('> ', end='')

        line: str = input()

        if line == '':
            return True

        if line == 'exit':
            return False

        if clparser.checkDecl(line):
            varDecl = clparser.parseDecl(line)
            self.__updateState(varDecl)
            return True

        cmds = clparser.parsePipes(line)
        cmds = list(map(lambda c: expansion(c, self.state), cmds))
        ostr = runCommand(cmds)

        print(ostr.getvalue())

        ostr.close()

        return True

    def __updateState(self, decl: clparser.VarDecl):
        self.state[decl.var] = decl.value
