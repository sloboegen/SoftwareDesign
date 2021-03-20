# SoftwareDesign

![GitHub Actions][github-actions-shield]

[github-actions-shield]: https://github.com/sloboegen98/SoftwareDesign/workflows/Build/badge.svg 
[![codecov](https://codecov.io/gh/sloboegen98/SoftwareDesign/branch/CLI/graph/badge.svg?token=LTFRIFM6FO)](https://codecov.io/gh/sloboegen98/SoftwareDesign)


## How to build

Firstly, you need to have Python interpreter **version 3.9**. **Earlier versions aren't supported**, because we use some new kinds of types in typehints.

Secondly, you need to install all dependencies:

```shell
make dev-deps
```

After that you can enter the following command for run:
```shell
make run
```

But, for the first time it's strongly recommended to run:
```shell
make
```

It runs all tests and linter.

## CLI overview

This CLI covers the small subset of Bash.
It has two types of expressions: command and variable declaration.

Also language support pipes, for example:

```shell
> cat file.txt | echo 42
42 
```

In original Bash it's correct to write a declaration between pipes, but it has no effect:

```shell
$ a=42
$ a=43 | echo $a
42
```

For simplify, in our CLI it's incorrect expression, it will be rejected by the parser.


### Commands

This CLI supports seven commands. They are truncated counterparts of their versions in Bash.

#### echo

Prints its arguments.

#### pwd

Prints the current folder.

#### cat

Prints the content of the file or of the input stream if there is no input file. Stand-alone `cat` command prints the content of the user input.

#### wc

Prints a count of lines, a count of words, a count of chars in the file or of the input stream if there is no input file. Stand-alone `wc` command prints same characteristics of the user input.

#### grep

Usage:
```shell
> grep [KEYS] PATTERNS [FILE]
```

`grep` searches for PATTERNS in FILE or in the input stream if there is no file.

`grep` supports following keys:

 * -i: is it need to match with case insensitive
 * -w: is it need to match a whole word
 * -A COUNT: the count of strings need to print after match

#### ls

`ls [FILE]` lists information about the FILEs on specified path
    (the current directory by default).

#### cd

`cd [PATH]` changes working directory to specified PATH.
    By default goes to `/home/{USERNAME}`.

#### exit

Ends the current session

### Variable declaration

Assigns the passed value to the variable. The declaration can't be used in pipe-expression, it can be stand alone only:

```shell
> a=1
> echo $a
1
```

```shell
> a=1 | echo $a
Parse error: ...
```

It's important to have no whitespace before and after sign equality.

### External process

Also you can call an external process from this CLI:

```shell
> cowsay 42
 ____
< 42 >
 ----
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||

```

```shell
> touch file.txt
> echo 42 43 | tee file.txt
file.txt
> cat file.txt
42 43
> cat file.txt | grep 42
42 43

```

## Architecture overview

CLI has four modules:

 * Session: holds all information current interpreter session and about variables

 * Parser(command line parser, clparser): checks an input for correctness, create intermediate representation for commands and declarations

 * Expanser: replace a variable by its value (depends on quotes) 
 
 * Executor: run the given command


More detailed description of architecture see in [description.md](./architecture/description.md)
