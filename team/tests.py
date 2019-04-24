from django.http import HttpRequest
from django.urls import resolve
from django.test import TestCase
from team.views import home_page

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found_view = resolve('/')
        self.assertEqual(found_view.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>Team Manager</title>', html)
        self.assertTrue(html.endswith('</html>'))
