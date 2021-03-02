from .session import Session


def main():
    session = Session()

    while True:
        try:
            _ = session.work()

        except (EOFError, KeyboardInterrupt):
            session.endSession()
            print('\nBye bye')
            break

        except Exception as e:
            print(str(e))
            continue


if __name__ == '__main__':
    main()
