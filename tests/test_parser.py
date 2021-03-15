import unittest

from src.clparser import CmdIR, VarDecl, getCmdParser
from src.clparser import parsePipes


class VarDeclTestCase(unittest.TestCase):
    def assertDeclTrue(self, line: str):
        self.assertTrue(VarDecl.checkDecl(line))

    def assertDeclFalse(self, line: str):
        self.assertFalse(VarDecl.checkDecl(line))

    def test_checkDeclTrue1(self):
        self.assertDeclTrue('a=1')

    def test_checkDeclTrue2(self):
        self.assertDeclTrue('a==1')

    def test_checkDeclTrue3(self):
        self.assertDeclTrue('a=!')

    def test_checkDeclTrue4(self):
        self.assertDeclTrue('a==')

    def test_checkDeclTrue5(self):
        self.assertDeclTrue('a=\'1\'')

    def test_checkDeclTrue6(self):
        self.assertDeclTrue('a=!')

    def test_checkDeclTrue7(self):
        self.assertDeclTrue('a="\'"')

    def test_checkDeclTrue8(self):
        self.assertDeclTrue('a=""')

    def test_checkDeclTrue9(self):
        self.assertDeclTrue('a=echo')

    def test_checkDeclTrue10(self):
        self.assertDeclTrue('a=')

    def test_checkDeclTrue11(self):
        self.assertDeclTrue('a=\n')

    def test_checkDeclFalse1(self):
        self.assertDeclFalse('a')

    def test_checkDeclFalse2(self):
        self.assertDeclFalse('a!=')

    def test_checkDeclFalse3(self):
        self.assertDeclFalse('echo 42')

    def test_checkDeclFalse4(self):
        self.assertDeclFalse('a=1 | echo 42')

    def test_pipe(self):
        self.assertDeclTrue('a="echo 42 | cat"')

    def test_checkDeclFalseChars(self):
        self.assertDeclFalse('a=|')
        self.assertDeclFalse('a=<')
        self.assertDeclFalse('a=>')
        self.assertDeclFalse('a=\'')
        self.assertDeclFalse('a="')


class CmdTestCase(unittest.TestCase):
    def assertCmdEqual(self, line: str, name: str,
                       args: list[str], keys: dict[str, str] = {}):
        def keysPrettyPrinter(keys: dict[str, str]) -> str:
            if not keys:
                return ''

            kpp = ''
            for k, v in keys.items():
                kv = f'{k} {v}'
                kv += ' ' if v else ''
                kpp += kv

            return kpp.rstrip()

        cmd: CmdIR = getCmdParser(line)

        kpp = keysPrettyPrinter(keys)

        argsStr: str = " ".join(args)

        gold = f'{name} {kpp} {argsStr}' if kpp else f'{name} {argsStr}'

        self.assertEqual(str(cmd), gold)
        self.assertEqual(cmd.name, name)
        self.assertEqual(cmd.args, args)
        self.assertEqual(cmd.keys, keys)

    def test_simple(self):
        line = 'echo 42'
        self.assertCmdEqual(line, 'echo', ['42'])

    def test_many_params(self):
        line = 'cat README.md nonexist.py'
        self.assertCmdEqual(line, 'cat', ['README.md', 'nonexist.py'])

    def test_with_key(self):
        line = 'grep -i 42 file.txt'
        self.assertCmdEqual(line, 'grep', ['42', 'file.txt'], {'-i': ''})

    def test_with_manykeys(self):
        line = 'grep -i -w 42 README.md'
        self.assertCmdEqual(line, 'grep',
                            ['42', 'README.md'], {'-i': '', '-w': ''})

    def test_with_kv(self):
        line = 'grep -A 10 42 README.md'
        self.assertCmdEqual(line, 'grep',
                            ['42', 'README.md'], {'-A': '10'})


class PipesTestCase(unittest.TestCase):
    def assertPipeEqual(self, line: str, cmds: list[str]):
        result = parsePipes(line)

        for testing, gold in zip(result, cmds):
            self.assertEqual(testing, gold)

    def test_simple(self):
        line = 'cat file.txt | cat file2.txt'
        result = ['cat file.txt', 'cat file2.txt']
        self.assertPipeEqual(line, result)

    def test_three(self):
        line = 'cat file.txt | cat file2.txt | echo 42'
        result = ['cat file.txt', 'cat file2.txt', 'echo 42']
        self.assertPipeEqual(line, result)

    def test_keys(self):
        line = 'cat file.txt | grep -i 42'
        result = ['cat file.txt', 'grep -i 42']
        self.assertPipeEqual(line, result)
