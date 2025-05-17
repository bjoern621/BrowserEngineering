import sys
import tkinter
from browser import Browser
from url import URL


def main():
    print("Hello, Browser Engineering!")

    url = sys.argv[1] if len(sys.argv) > 1 else "http://example.com/"

    Browser().load(URL(url))

    tkinter.mainloop()


if __name__ == "__main__":
    main()
