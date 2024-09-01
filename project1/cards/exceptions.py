class DeckEmptyException(Exception):
    """
    Custom exception to handle cases where a deck is empty and a redirect is needed.

    :param redirect_url: The URL to which the user should be redirected.
    """

    def __init__(self, redirect_url):
        self.redirect_url = redirect_url
        super().__init__(f'Redirecting to {redirect_url}')
