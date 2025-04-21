import socket


class URL:
    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)

        assert self.scheme == "http", "Only HTTP scheme is supported"

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

    def request(self) -> str:
        # Request

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        s.connect((self.host, 80))

        request = f"GET {self.path} HTTP/1.0\r\n"
        request += f"Host: {self.host}\r\n"
        request += "\r\n"

        s.send(request.encode("utf-8"))

        # Response

        response = s.makefile("r", encoding="utf-8", newline="\r\n")

        statusline = response.readline()
        version, status_code, reason = statusline.split(" ", 2)  # type: ignore

        headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            name, value = line.split(":", 1)
            headers[name.casefold()] = value.strip()

        assert (
            "transfer-encoding" not in headers
        ), "Chunked transfer encoding is not supported"
        assert "content-encoding" not in headers, "Content encoding is not supported"

        content = response.read()

        s.close()

        return content
