"""Main file for project."""

import os

from setup import prepare_project_directory


def main() -> None:
    """Main function for project."""
    prepare_project_directory()
    print(os.getcwd())


if __name__ == "__main__":
    main()
