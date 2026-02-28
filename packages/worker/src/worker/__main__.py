import sys


def main() -> None:
    sys.argv = ["taskiq", "worker", "worker.runner:broker"]
    from taskiq.__main__ import main as taskiq_main
    taskiq_main()


if __name__ == "__main__":
    main()
