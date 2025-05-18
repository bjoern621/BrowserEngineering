import sys
import tkinter
import os
from browser import Browser
from url import URL


def main():
    print("Hello, Browser Engineering!")

    working_directory = os.getcwd()
    path_to_example = working_directory + "/example.html"

    url = sys.argv[1] if len(sys.argv) > 1 else "file://" + path_to_example

    Browser().load(URL(url))

    tkinter.mainloop()


if __name__ == "__main__":
    main()
