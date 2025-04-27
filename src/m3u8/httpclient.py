import ssl
import urllib2

from urlparse import urljoin


class DefaultHTTPClient:
    def __init__(self, proxies=None):
        self.proxies = proxies

    def download(self, uri, timeout=None, headers={}, verify_ssl=True):
        proxy_handler = urllib2.ProxyHandler(self.proxies)
        https_handler = urllib2.HTTPSHandler()
        opener = urllib2.build_opener(proxy_handler, https_handler)
        opener.addheaders = headers.items()
        resource = opener.open(uri, timeout=timeout)
        base_uri = urljoin(resource.geturl(), ".")
        content = resource.read().decode(
            resource.headers.getparam('charset') or 'utf-8'
        )
        return content, base_uri


class HTTPSHandler:
    def __new__(self, verify_ssl=True):
        context = ssl.create_default_context()
        if not verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return urllib2.HTTPSHandler(context=context)
