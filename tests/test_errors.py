from .test_cli import CmdTestCase
from io import StringIO
from src.session import Session


class ErrorTestCase(CmdTestCase):
    def _execCommands(self, line: list[str]) -> str:
        result: StringIO = StringIO()

        for cmd in line:
            result = self.session.getCmdResult(cmd)

        return result.getvalue().rstrip()

    def assertErrorMsgEquals(self, line: list[str], expected: str):
        try:
            self._execCommands(line)
        except Exception as e:
            err_msg = str(e)
            self.assertEqual(err_msg, expected)

    def setUp(self) -> None:
        self.session = Session()

    def tearDown(self) -> None:
        self.session.endSession()

    def test_cat2(self):
        p = ['cat foo goo']
        self.assertErrorMsgEquals(
            p, 'cat: cat supports only one file, but given 2')

    def test_wc2(self):
        p = ['wc foo goo']
        self.assertErrorMsgEquals(
            p, 'wc: wc supports only one file, but given 2')

    def test_external1(self):
        p = ['ping foo']
        self.assertErrorMsgEquals(
            p, 'ping: foo: Temporary failure in name resolution')

    def test_external2(self):
        p = ['ababab']
        self.assertErrorMsgEquals(
            p, '[Errno 2] No such file or directory: \'ababab\'')
