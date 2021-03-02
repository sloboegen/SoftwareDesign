def expansion(cmd: str, state: dict[str, str]) -> str:
    """
    Interpolates each variable by its value from state,
    except variable in single quotes

    Args:
        cmd (str): user input
        state (dict[str, str]): variable name -> value

    Returns:
        command where each variable replaced with its value
        variables in single quotes are not interpolated

    Examples:
        >>> expansion('echo $a', {'a' : 1})
        1
        >>> expansion('echo "$a"', {'a' : 1})
        1
        >>> expansion('echo \'$a\'', {'a' : 1}))
        $a
        >>> expansion('echo "\'$a\'"', {'a' : 1})
        '1'
        >>> expansion('echo \'"$a"\', {'a' : 1})
        "$a"
        >>> expansion('echo $a', {})
        empty-string

    """

    inSingleQuote: bool
    inDoubleQuote: bool
    startVar: bool
    inSingleQuote, inDoubleQuote, startVar = [False] * 3

    expansed: str = ''
    curVar: str = ''

    for sym in cmd:
        if sym == "'" and not inDoubleQuote:
            inSingleQuote ^= True
            continue

        if sym == '"' and not inSingleQuote:
            inDoubleQuote ^= True
            continue

        if sym == '$' and not inSingleQuote:
            # for example, `$x$y`
            if startVar:
                expansed += state.setdefault(curVar, '')
                curVar = ''

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

    return expansed
