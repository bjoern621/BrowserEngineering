from .url import URL


def main():
    print("Hello, Browser Engineering!")

    url = "http://example.com"
    load(URL(url))


def show(body: str):
    in_tag = False
    for char in body:
        if char == "<":
            in_tag = True
        elif char == ">":
            in_tag = False
        elif not in_tag:
            print(char, end="")


def load(url: URL):
    body: str = url.request()
    show(body)


if __name__ == "__main__":
    main()
