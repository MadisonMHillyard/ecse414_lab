from src.registry import AICN_Registry


def main():

    # instantiate registry
    registry = AICN_Registry()

    # start registry thread
    registry.start()

    # wait for registry thread to end (never)
    registry.join()


if __name__ == '__main__':
    main()




