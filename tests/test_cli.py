import shutil
import unittest
import os
import subprocess

from io import StringIO
from pathlib import Path

from src.session import Session


class CmdTestCase(unittest.TestCase):
    def _execCommands(self, line: list[str]) -> str:
        result: StringIO = StringIO()

        for cmd in line:
            result = self.session.getCmdResult(cmd)

        return result.getvalue().rstrip()

    def assertCmdResult(self, lines: list[str], result: str) -> None:
        self.assertEqual(self._execCommands(lines), result)

    def assertThrows(self, lines:list[str], result: str) -> None:
        try:
            self._execCommands(lines)
        except ValueError as err:
            self.assertEqual(str(err), result)

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

    def test_not_pipe(self):
        cmd = ['echo "asd|asd"']
        self.assertCmdResult(cmd, 'asd|asd')


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

    def test_pipes(self):
        cmd = ['echo 42 | cat']

        self.assertCmdResult(cmd, '42')


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

    def test_pipes(self):
        p = self._getCorrectPath('/files/random')
        cmd = [f'cat {p} | wc']

        self.assertCmdResult(cmd, '5 40 253')

    def test_pipes_echo(self):
        cmd = ['echo 123 | wc']
        self.assertCmdResult(cmd, '1 1 4')


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


class LsTestCase(CmdTestCase):
    def setUp(self) -> None:
        self.session = Session()
        self.cur_dir = os.getcwd()
        make_testing_directory(self.cur_dir)

    def tearDown(self) -> None:
        self.session.endSession()
        remove_testing_directory(self.cur_dir)

    def test_local(self):
        path = ''
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [])

        self.assertCmdResult(cmd, gold)

    def test_local2(self):
        path = '.'
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [path])

        self.assertCmdResult(cmd, gold)

    def test_subdir(self):
        path = 'src'
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [path])

        self.assertCmdResult(cmd, gold)

    def test_external(self):
        path = '..'
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [path])

        self.assertCmdResult(cmd, gold)

    def test_home(self):
        path = '~'
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [str(Path.home())])  # ~ doesn't seem to go to system ls properly

        self.assertCmdResult(cmd, gold)

    def test_file(self):
        path = 'README.md'
        cmd = [f'ls {path}']
        gold = self.getExternalResult('ls', [path])

        self.assertCmdResult(cmd, gold)


def make_testing_directory(path):
    testing_dir = os.path.join(path, "test")
    testing_subdir1 = os.path.join(testing_dir, "test1")
    testing_subdir2 = os.path.join(testing_dir, "test2")
    file1 = os.path.join(testing_dir, "file1.txt")
    file2 = os.path.join(testing_subdir2, "file2.txt")

    os.makedirs(testing_dir, exist_ok=True)
    os.makedirs(testing_subdir1, exist_ok=True)
    os.makedirs(testing_subdir2, exist_ok=True)
    with open(file1, "w") as file:
        file.write("file1")

    with open(file2, "w") as file:
        file.write("file2")


def remove_testing_directory(path):
    testing_dir = os.path.join(path, "test")
    shutil.rmtree(testing_dir)


class CdTestCase(CmdTestCase):
    def setUp(self) -> None:
        self.session = Session()
        self.cur_dir = os.getcwd()
        self.reset = [f'cd {self.cur_dir}']
        make_testing_directory(self.cur_dir)

    def tearDown(self) -> None:
        self.session.endSession()
        remove_testing_directory(self.cur_dir)

    def test_homing(self):
        cmd = ['cd', 'pwd']

        self.assertCmdResult(cmd, str(Path.home()))
        self._execCommands(self.reset)

    def test_folder(self):
        gold = self.getExternalResult('ls', ['test'])
        cmd = ['cd test', 'ls']

        self.assertCmdResult(cmd, gold)
        self._execCommands(self.reset)

    def test_subfolder(self):
        gold = self.getExternalResult('ls', ['test/test2'])
        cmd = ['cd test/test2', 'ls']

        self.assertCmdResult(cmd, gold)
        self._execCommands(self.reset)

    def test_empty_subfolder(self):
        gold = self.getExternalResult('ls', ['test/test1'])
        cmd = ['cd test/test1', 'ls']

        self.assertCmdResult(cmd, gold)
        self._execCommands(self.reset)

    def test_there_and_back_again(self):
        self._execCommands(['cd test'])
        gold = self.getExternalResult('ls', ['..'])
        smaug = self.getExternalResult('ls', ['.'])
        cmd = ['cd ..', 'ls']
        self.assertCmdResult(cmd, gold)
        cmd = ['cd test', 'ls']

        self.assertCmdResult(cmd, smaug)
        self._execCommands(self.reset)

    def test_file(self):
        path = 'test/file1.txt'
        cmd = [f'cd {path}']

        self.assertThrows(cmd, f'cd: {path}: Not a directory')
        self._execCommands(self.reset)

    def test_nonex(self):
        path = 'test/file2.txt'
        cmd = [f'cd {path}']

        self.assertThrows(cmd, f'cd: {path}: No such file or directory')
        self._execCommands(self.reset)


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
