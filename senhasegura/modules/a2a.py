from senhasegura.utils.auth import Auth
import requests
import re


class A2A(Auth):
    def __init__(self, hostname: str, auth_type: str, **auth_params) -> None:
        http_methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
        self.__methods = {method: getattr(requests, method.lower()) for method in http_methods}
        self.__hostname = self.__validate_hostname(hostname)
        super().__init__(auth_type, **auth_params)

        [setattr(self, method.lower(),
                 (lambda m: lambda endpoint, **kwargs: self.__request(m, endpoint, **kwargs))(method))
         for method in http_methods]

    def __is_valid_hostname_string(self, hostname: str) -> str:

        regex = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-){0,126}$", re.IGNORECASE)
        if not all(regex.match(x) for x in hostname.rstrip(".").split(".")):
            raise ValueError('invalid hostname string: "%s"' % hostname)
        return hostname

    def __validate_hostname(self, hostname: str) -> bool:
        hostname = f"https://{self.__is_valid_hostname_string(hostname)}"
        response = requests.head(hostname)
        response.raise_for_status()
        return hostname

    def __is_valid_endpoint_string(self, endpoint: str) -> bool:
        if not re.match( r'^(?!.*//)([a-zA-Z0-9_\-./%?&=]*)?$', endpoint):
            raise ValueError('invalid endpoint string: "%s"' % endpoint)
        return endpoint

    def __request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        if method.upper() not in self.__methods:
            raise ValueError('Invalid HTTP method: "%s"' % method)

        url = f"{self.__hostname}/{self.__is_valid_endpoint_string(endpoint).lstrip('/')}"
        return self.__methods[method.upper()](url, auth=self._Auth__auth, **kwargs)
