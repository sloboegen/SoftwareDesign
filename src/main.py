from .session import Session


def main():
    try:
        session = Session()
        while session.work():
            pass

    except (EOFError, KeyboardInterrupt):
        print('\nBye bye')


if __name__ == '__main__':
    main()
