import socket


class URL:
    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)

        assert self.scheme in (
            "http",
            "https",
            "file",
        ), "Only HTTP, HTTPS and FILE schemes are supported"

        if self.scheme == "file":
            self.host = ""
            self.path = url

            return

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if "/" not in url:
            url += "/"

        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self) -> str:
        """
        Sends a GET request for http/https URLs or reads a local file for file URLs.
        Returns the content as a string. For http/https URLs, the content is the response body (without headers).
        """

        if self.scheme == "file":
            # Read local file
            with open(self.path, "r", encoding="utf-8") as file:
                return file.read()

        # Request

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        s.connect((self.host, self.port))

        if self.scheme == "https":
            import ssl

            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

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

    def resolve(self, url: str):
        """
        Resolves a URL string relative to the current URL.
        This method handles various URL formats:
        - Absolute URLs with protocol (e.g., "http://example.com")
        - Protocol-relative URLs (scheme-relative) (e.g., "//example.com")
        - Absolute paths (host-relative) (e.g., "/path")
        - Relative paths (path-relative) (e.g., "path")
        Returns:
            URL: A new URL object with an absolute URL.
        """

        if "://" in url:
            # Absolute URL
            return URL(url)

        if not url.startswith("/"):
            # Absolute path (host-relative)
            dir, _ = self.path.rsplit("/", 1)

            while url.startswith("../"):
                # Go up one directory for each "../"
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
                url = url[3:]

            url = f"{dir}/{url}"

        if url.startswith("//"):
            # Protocol-relative URL (scheme-relative)
            return URL(f"{self.scheme}:{url}")
        else:
            # Relative path (path-relative)
            return URL(f"{self.scheme}://{self.host}:{str(self.port)}{url}")
