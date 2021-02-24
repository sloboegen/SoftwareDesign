def expansion(cmdline: str, state: dict[str, str]) -> str:
    """
    Interpolates each variable by its value from state,
    except variable in single quotes

    Args:
        cmd (str): a command name and its arguments
        state (dict[str, str]): variable name -> value

    Returns:
        str: command where each variable replaced with its value
        variables in single quotes are not interpolated

    Examples:
        >>> expansion('$a', {'a' : 1})
        1
        >>> expansion('"$a"', {'a' : 1})
        echo 1
        >>> expansion('\'$a\'', {'a' : 1}))
        $a
        >>> expansion('"\'$a\'"', {'a' : 1})
        '1'
        >>> expansion('\'"$a"\', {'a' : 1})
        "$a"
        >>> expansion('$a', {})
        empty-string

    """

    inSingleQuote: bool
    inDoubleQuote: bool
    startVar: bool
    inSingleQuote, inDoubleQuote, startVar = [False] * 3

    expansed: str = ''
    curVar: str = ''

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

    return expansed
