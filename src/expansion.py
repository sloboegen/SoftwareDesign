from clparser import CmdIR

# [(a, 1)] |- $a => 1
# [(a, 1)] |- "$a" => 1
# [(a, 1)] |- \"$a\" => "1"
# [(a, 1)] |- '$a' => $a
# [(a, 1)] |- "'$a'" => '1'
# [(a, 1)] |- '"$a"' => "$a"
# [(a, 1)] |- "'"$a"'"" => '1'


def expansion(cmd: CmdIR, state: dict[str, str]) -> str:
    inSingleQuote: bool
    inDoubleQuote: bool
    startVar: bool
    inSingleQuote, inDoubleQuote, startVar = [False] * 3

    expansed: str = ''
    curVar: str = ''

    cmdline = cmd.name + ' ' + cmd.args

    for sym in cmdline:
        if sym == "'" and not inDoubleQuote:
            inSingleQuote ^= True
            continue

        if sym == '"' and not inSingleQuote:
            inDoubleQuote ^= True
            continue

        if sym == '$' and not inSingleQuote:
            startVar = True
            continue

        if startVar:
            if sym not in ["'", '"', ' ']:
                curVar += sym
                continue

            expansed += state.setdefault(curVar, '')
            curVar = ''
            startVar = False

            if sym == "'" and inDoubleQuote:
                expansed += "'"

            if sym == '"' and inSingleQuote:
                expansed += '"'

            if sym == ' ':
                expansed += ' '

            continue

        expansed += sym

    if startVar:
        expansed += state.setdefault(curVar, '')
        curVar = ''
        startVar = False

    return CmdIR(expansed)
