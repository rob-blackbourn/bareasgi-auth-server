"""Entrypoint for starting the server"""

import sys
from bareasgi_auth_server import start_server


def main():
    start_server(sys.argv)


if __name__ == "__main__":
    main()