import unittest

from src.clparser import CmdIR, VarDecl
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

    def test_checkDeclFalseChars(self):
        self.assertDeclFalse('a=|')
        self.assertDeclFalse('a=<')
        self.assertDeclFalse('a=>')
        self.assertDeclFalse('a=\'')
        self.assertDeclFalse('a="')


class CmdTestCase(unittest.TestCase):
    def assertCmdEqual(self, line: str, name: str, args: str):
        cmd: CmdIR = CmdIR(line)
        self.assertEqual(str(cmd), f'{name} {args}')
        self.assertEqual(cmd.name, name)
        self.assertEqual(cmd.args, cmd.args)

    def test_simple(self):
        line = 'echo 42'
        self.assertCmdEqual(line, 'echo', '42')

    def test_many_params(self):
        line = 'cat README.md nonexist.py'
        self.assertCmdEqual(line, 'cat', 'README.md nonexist.py')


class PipesTestCase(unittest.TestCase):
    def assertPipeEqual(self, line: str, cmds: list[str]):
        cmdsIR = [CmdIR(c) for c in cmds]
        result = parsePipes(line)

        for testing, gold in zip(result, cmdsIR):
            self.assertTrue(testing == gold)

    def test_simple(self):
        line = 'cat file.txt | cat file2.txt'
        result = ['cat file.txt', 'cat file2.txt']
        self.assertPipeEqual(line, result)

    def test_three(self):
        line = 'cat file.txt | cat file2.txt | echo 42'
        result = ['cat file.txt', 'cat file2.txt', 'echo 42']
        self.assertPipeEqual(line, result)
