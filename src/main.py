from .session import Session


def main():
    try:
        session = Session()
        while session.work():
            pass

        session.endSession()

    except (EOFError, KeyboardInterrupt):
        print('\nBye bye')


if __name__ == '__main__':
    main()
