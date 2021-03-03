from io import StringIO
from .executor import runCommand
from .expansion import expansion
from .clparser import CmdIR, parsePipes, VarDecl


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

        splitByPipes: list[str] = parsePipes(line)

        expansed: list[str] = [expansion(c, self.state) for c in splitByPipes]

        isDecl: bool = (len(expansed) == 1 and VarDecl.checkDecl(expansed[0]))

        if isDecl:
            varDecl = VarDecl.parseDecl(expansed[0])
            self.__updateState(varDecl)

            return StringIO('')

        cmds = [CmdIR(c) for c in expansed]

        try:
            ostr = runCommand(cmds)
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

        if line == '' or line.isspace():
            return True

        ostr = self.getCmdResult(line)

        print(ostr.getvalue(), end='')

        ostr.close()

        return True

    def __updateState(self, decl: VarDecl):
        self.state[decl.var] = decl.value

    def endSession(self) -> None:
        self.state.clear()
