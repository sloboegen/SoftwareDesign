from io import StringIO
from .executor import runCommand
from .expansion import expansion
from .clparser import createCmdIR, parsePipes, VarDecl


class Session():
    """
    This class is responsible for current session.
    It holds an environment (map the variable name to its value)

    Attributes:
        state (dict[str, str]): map the variable name to its value

    """

    def __init__(self) -> None:
        self.state: dict[str, str]
        self.state = dict()

    def getCmdResult(self, line: str) -> StringIO:
        """
        Run command and return stream with the result

        Args:
            line (str): the user entered command

        Returns:
            StringIO: the stream with the result of cmd execution

        """

        if VarDecl.checkDecl(line):
            varDecl = VarDecl.parseDecl(line)
            self.__updateState(varDecl)

            return StringIO('')

        cmds: list[str]
        cmds = parsePipes(line)
        cmds = [expansion(c, self.state) for c in cmds]
        cmdsIR = createCmdIR(cmds)

        try:
            ostr = runCommand(cmdsIR)
        except Exception as e:
            raise e

        return ostr

    def work(self) -> bool:
        """
        Like as eventloop

        Args:
            No arguments

        Returns:
            bool: False if it's impossible to continue this session
                  True otherwise

        """

        print('> ', end='')

        line: str = input()

        if line == '':
            return True

        # if line == 'exit':
        #     raise EOFError

        ostr = self.getCmdResult(line)

        print(ostr.getvalue(), end='')

        ostr.close()

        return True

    def __updateState(self, decl: VarDecl):
        self.state[decl.var] = decl.value

    def endSession(self) -> None:
        self.state.clear()
