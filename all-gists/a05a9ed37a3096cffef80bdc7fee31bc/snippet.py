"""Clean all experiments in a PyCrayon server."""
from pycrayon import CrayonClient


def main():
    client = CrayonClient()
    client.remove_all_experiments()


if __name__ == '__main__':
    main()
