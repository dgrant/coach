from django.test import TestCase

from team.models import Team

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_POST_request(self):
        response = self.client.post('/', data={'team_name': 'Grey Wolves'})
        self.assertIn('Grey Wolves', response.content.decode())
        self.assertTemplateUsed(response, 'home.html')


class TeamModelTest(TestCase):

    def test_saving_and_retrieving_team(self):
        first_team = Team()
        first_team.name = "my team"
        first_team.save()

        second_team = Team()
        second_team.name = "other team"
        second_team.save()

        self.assertEqual(2, Team.objects.count())

        teams = Team.objects.all()
        self.assertEqual(first_team.name, teams[0].name)
        self.assertEqual(second_team.name, teams[1].name)
