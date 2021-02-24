import unittest
import os
import subprocess

from io import StringIO
from src.session import Session


class CmdTestCase(unittest.TestCase):
    def _execCommands(self, line: list[str]) -> str:
        result: StringIO = StringIO()

        for cmd in line:
            result = self.session.getCmdResult(cmd)

        return result.getvalue().rstrip()

    def assertCmdResult(self, lines: list[str], result: str) -> None:
        self.assertEqual(self._execCommands(lines), result)

    def _getCorrectPath(self, relPath: str) -> str:
        rp = os.path.dirname(__file__) + relPath
        return os.path.abspath(rp)

    def getExternalResult(self, name: str, args: list[str],
                          istream: StringIO = StringIO()) -> str:
        externalProcess = subprocess.Popen([name, *args],
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

        encodedInput = bytes(istream.getvalue().encode('utf-8'))
        externalProcess.stdin.write(encodedInput)
        result = externalProcess.communicate()[0].decode('utf-8')
        result = result.rstrip()

        return result

    def setUp(self) -> None:
        self.session = Session()

    def tearDown(self) -> None:
        self.session.endSession()


class EchoTestCase(CmdTestCase):
    def test_ws(self):
        cmd = ['echo \' \'']
        self.assertCmdResult(cmd, '')

    def test_simple(self):
        cmd = ['echo 42']
        self.assertCmdResult(cmd, '42')

    def test_string(self):
        cmd = ['echo "abc"']
        self.assertCmdResult(cmd, 'abc')

    def test_many_args(self):
        cmd = ['echo abc 1 2']
        self.assertCmdResult(cmd, 'abc 1 2')

    def test_variables1(self):
        cmd = ['a=1', 'echo $a']
        self.assertCmdResult(cmd, '1')

    def test_variables2(self):
        cmd = ['a=1', 'a=2', 'echo $a']
        self.assertCmdResult(cmd, '2')

    def test_variable3(self):
        cmd = ['echo $a']
        self.assertCmdResult(cmd, '')

    def test_variable4(self):
        cmd = ['a=1', 'b=2', 'echo $a $b']
        self.assertCmdResult(cmd, '1 2')

    def test_variables5(self):
        cmd = ['a=echo', 'b=abc', '$a $b']
        self.assertCmdResult(cmd, 'abc')

    def test_variables6(self):
        cmd = ['a==', 'echo $a']
        self.assertCmdResult(cmd, '=')

    def test_quotes1(self):
        cmd = ['echo \'abc\'']
        self.assertCmdResult(cmd, 'abc')

    def test_quotes2(self):
        cmd = ['echo \'$a\'']
        self.assertCmdResult(cmd, '$a')

    def test_quotes3(self):
        cmd = ['a=1', 'echo "$a"']
        self.assertCmdResult(cmd, '1')

    def test_quotes4(self):
        cmd = ['a=1', 'b=2', 'echo \'$a\' "$b"']
        self.assertCmdResult(cmd, '$a 2')

    def test_quotes5(self):
        cmd = ['a=1', 'b=2', 'echo \'$a $b\'']
        self.assertCmdResult(cmd, '$a $b')

    def test_quotes6(self):
        cmd = ['a=\'!\'', 'echo $a']
        self.assertCmdResult(cmd, '!')

    def test_pipes1(self):
        cmd = ['echo 42 | echo']
        self.assertCmdResult(cmd, '')

    def test_pipes2(self):
        cmd = ['echo 42 | echo 43 44']
        self.assertCmdResult(cmd, '43 44')


class PwdTestCase(CmdTestCase):
    def test_pwd(self):
        cmd = ['pwd']
        gold = os.getcwd()
        self.assertCmdResult(cmd, gold)


class CatTestCase(CmdTestCase):
    def test_empty(self):
        p = self._getCorrectPath('/files/empty')
        cmd = [f'cat {p}']
        self.assertCmdResult(cmd, '')

    def test_byte(self):
        p = self._getCorrectPath('/files/bytes')
        cmd = [f'cat {p}']
        with open(p) as f:
            gold = f.read()

        self.assertCmdResult(cmd, gold)


class WcTestCase(CmdTestCase):
    def test_empty(self):
        p = self._getCorrectPath('/files/empty')
        cmd = [f'wc {p}']

        self.assertCmdResult(cmd, f'0 0 0 {p}')

    def test_byte(self):
        p = self._getCorrectPath('/files/bytes')
        cmd = [f'wc {p}']

        self.assertCmdResult(cmd, f'1 200 1168 {p}')

    def test_lines(self):
        p = self._getCorrectPath('/files/lines')
        cmd = [f'wc {p}']

        self.assertCmdResult(cmd, f'6 0 6 {p}')


class GrepTestCase(CmdTestCase):
    def _runGrepFile(self, pattern: str, filename: str,
                     keys: list[str] = []) -> str:
        istream = StringIO()

        with open(filename, 'r') as f:
            istream.write(f.read())

        result = self.getExternalResult('grep', [*keys, pattern], istream)
        return result

    def test_simple(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'It'
        cmd = [f'grep {pattern} {p}']
        gold = self._runGrepFile(pattern, p)

        self.assertCmdResult(cmd, gold)

    def test_case_insensitive(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'What'
        cmd = [f'grep -i {pattern} {p}']
        gold = self._runGrepFile(pattern, p, ['-i'])

        self.assertCmdResult(cmd, gold)

    def test_whole_word(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'It'
        cmd = [f'grep -w {pattern} {p}']
        gold = self._runGrepFile(pattern, p, ['-w'])

        self.assertCmdResult(cmd, gold)

    def test_after_match(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'What'
        cmd = [f'grep -A 2 {pattern} {p}']
        gold = self._runGrepFile(pattern, p, ['-A 2'])

        self.assertCmdResult(cmd, gold)

    def test_two_keys_iw(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'What'
        cmd = [f'grep -i -w {pattern} {p}']
        gold = self._runGrepFile(pattern, p, ['-i', '-w'])

        self.assertCmdResult(cmd, gold)

    def test_two_keys_aw(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'What'
        cmd = [f'grep -A 2 -i {pattern} {p}']
        gold = self._runGrepFile(pattern, p, ['-A 2', '-i'])

        self.assertCmdResult(cmd, gold)

    def test_pipe(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'What'
        cmd = [f'cat {p} | grep -i {pattern}']
        gold = self._runGrepFile(pattern, p, ['-i'])

        self.assertCmdResult(cmd, gold)

    def test_pipe2(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'If'
        cmd = [f'cat {p} | grep -A 2 -w {pattern}']
        gold = self._runGrepFile(pattern, p, ['-A 2', '-w'])

        self.assertCmdResult(cmd, gold)

    def test_var(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'If'
        cmd = [f'pat={pattern}', f'cat {p} | grep -A 2 -w $pat']
        gold = self._runGrepFile(pattern, p, ['-A 2', '-w'])

        self.assertCmdResult(cmd, gold)

    def test_regex1(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = 'par*'
        cmd = [f'grep {pattern} {p}']
        gold = self._runGrepFile(pattern, p)

        self.assertCmdResult(cmd, gold)

    def test_regex2(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = '[pr]ain'
        cmd = [f'grep {pattern} {p}']
        gold = self._runGrepFile(pattern, p)

        self.assertCmdResult(cmd, gold)

    def test_regex3(self):
        p = self._getCorrectPath('/files/kafka.txt')
        pattern = '.*in.*'
        cmd = [f'grep {pattern} {p}']
        gold = self._runGrepFile(pattern, p)

        self.assertCmdResult(cmd, gold)


class ExternalTestCase(CmdTestCase):
    def test_cowsay(self):
        cmd = ['cowsay privetiki']
        gold = self.getExternalResult('cowsay', ['privetiki'])
        self.assertCmdResult(cmd, gold)

    def test_read_file(self):
        cmd = ['touch file.txt',
               'echo 42 | tee file.txt',
               'cat file.txt']
        self.assertCmdResult(cmd, '42')

        subprocess.run(['rm', 'file.txt'])  # delete created file
