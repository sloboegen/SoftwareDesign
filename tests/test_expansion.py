import unittest
from src.expansion import expansion


class ExpansionTestCase(unittest.TestCase):
    def assertExpansion(self, line: str, state: dict[str, str], result: str):
        expansed: str = str(expansion(line, state))
        self.assertEqual(expansed, result)

    def test_simple(self):
        line = 'echo $a'
        state = {'a': '42'}
        gold = 'echo 42'
        self.assertExpansion(line, state, gold)

    def test_quotes1(self):
        line = 'echo "$a"'
        state = {'a': '42'}
        gold = 'echo 42'
        self.assertExpansion(line, state, gold)

    def test_quotes2(self):
        line = 'echo \'$a\''
        state = {'a': '42'}
        gold = 'echo $a'
        self.assertExpansion(line, state, gold)

    def test_quotes3(self):
        line = 'echo "\'$a\'"'
        state = {'a': '42'}
        gold = 'echo \'42\''
        self.assertExpansion(line, state, gold)

    def test_quotes4(self):
        line = 'echo \'"$a"\''
        state = {'a': '42'}
        gold = 'echo "$a"'
        self.assertExpansion(line, state, gold)

    def test_empty_state(self):
        line = 'echo $a'
        state = dict()
        gold = 'echo '
        self.assertExpansion(line, state, gold)

    def test_concat(self):
        line = '$x$y'
        state = {'x': 'ex', 'y': 'it'}
        gold = 'exit'
        self.assertExpansion(line, state, gold)
