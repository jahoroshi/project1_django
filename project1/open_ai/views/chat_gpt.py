import openai
import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# If in DEBUG mode, set up Django settings
if settings.DEBUG:
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_1.settings')
    django.setup()

# Proxy configuration for requests
PROXY = {
    "http": "socks5://45.138.87.238:1080",
    "https": "socks5://23.19.244.109:1080",
}


class OpenAiChatGpt:
    """
    A class to interact with OpenAI's ChatGPT API using optional session management and proxy settings.
    """

    def __init__(self, api_key: str, proxy: dict = None, use_session: bool = False):
        """
        Initialize the OpenAiChatGpt instance.

        :param api_key: The API key for authenticating with OpenAI.
        :param proxy: A dictionary specifying the proxy settings for HTTP and HTTPS.
        :param use_session: Boolean flag to determine if a session should be used for requests.
        """
        self.proxy = proxy
        self.use_session = use_session
        self.api_key = api_key
        openai.api_key = self.api_key

        if self.use_session and self.proxy:
            self._create_session()

    def _create_session(self):
        """
        Create and configure a requests session with retry logic and proxy settings.
        """
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.proxies.update(self.proxy)

        # Set the session in OpenAI's request handling
        openai.requestssession = session

    def chatgpt_single_call(self, system_content: str, user_content: str, model: str = "gpt-4o-mini") -> str:
        """
        Make a single call to the OpenAI ChatGPT API.

        :param system_content: The system message providing instructions or context to the model.
        :param user_content: The user message or prompt to the model.
        :param model: The OpenAI model to use (default is "gpt-4o-mini").
        :return: The response content from the model.
        """
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            temperature=1,
            top_p=0.8,
        )
        return completion['choices'][0]['message']['content']


# Instantiate the OpenAiChatGpt client with the provided API key and proxy settings
chatgpt_client = OpenAiChatGpt(api_key=settings.OPENAI_API_KEY, proxy=PROXY, use_session=settings.DEBUG)
