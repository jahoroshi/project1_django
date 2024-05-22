class DeckEmptyException(Exception):
    def __init__(self, redirect_url):
        self.redirect_url = redirect_url
        super().__init__(f'Redirecting to {redirect_url}')