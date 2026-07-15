import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def get_clean_session():
    session = requests.Session()
    # Это ключевая строка: игнорируем HTTP_PROXY/HTTPS_PROXY из системы
    session.trust_env = False

    retry = Retry(
        total=10,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
