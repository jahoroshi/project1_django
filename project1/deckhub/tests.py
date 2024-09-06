from django.test import TestCase
from django.urls import reverse
from users.models import User
from cards.models import Categories

class DecksListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.client.login(username='testuser@user.com', email='testuser@user.com', password='testpass')
        Categories.objects.create(name='Deck 0', user=self.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/deck/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('decks_list'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('decks_list'), follow=True)
        self.assertTemplateUsed(response, 'deckhub/decks_list.html')

    def test_view_returns_correct_data(self):
        response = self.client.get(reverse('decks_list'), follow=True)
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(response.context['object_list'][0].name, 'Deck 0')


class DeckCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.client.login(username='testuser@user.com', email='testuser@user.com', password='testpass')

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('deck_create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('deck_create'))
        self.assertTemplateUsed(response, 'deckhub/deck_form.html')

    def test_view_creates_deck(self):
        response = self.client.post(reverse('deck_create'), {'name': 'New Deck'})
        self.assertEqual(Categories.objects.count(), 1)
        self.assertEqual(Categories.objects.first().name, 'New Deck')


class DeckUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.client.login(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.deck = Categories.objects.create(name='Deck 4', user=self.user)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('deck_edit', kwargs={'pk': self.deck.pk}))
        self.assertEqual(response.status_code, 200)



class DeckContentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.client.login(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.deck = Categories.objects.create(name='Deck 3', user=self.user)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('deck_content', kwargs={'slug': self.deck.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('deck_content', kwargs={'slug': self.deck.slug}))
        self.assertTemplateUsed(response, 'deckhub/deck_content.html')


class DeckDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.client.login(username='testuser@user.com', email='testuser@user.com', password='testpass')
        self.deck = Categories.objects.create(name='Deck 2', user=self.user)

    def test_delete_deck(self):
        response = self.client.post(reverse('deck_delete', kwargs={'slug': self.deck.slug}))
        self.assertEqual(Categories.objects.count(), 0)
        self.assertRedirects(response, reverse('decks_list'))