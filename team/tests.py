from django.test import TestCase


class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_POST_request(self):
        response = self.client.post('/', data={'team_name': 'Grey Wolves'})
        self.assertIn('Grey Wolves', response.content.decode())
        self.assertTemplateUsed(response, 'home.html')
