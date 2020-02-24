from django.test import TestCase

from team.models import Team

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_POST_request(self):
        response = self.client.post('/', data={'team_name': 'Grey Wolves'})

        self.assertEqual(1, Team.objects.count())
        new_item = Team.objects.first()
        self.assertEqual(new_item.name, "Grey Wolves")

    def test_redirects_after_POST(self):
        response = self.client.post('/', data={'team_name': 'Grey Wolves'})
        self.assertEqual(302, response.status_code)
        self.assertEqual("/", response["location"])

    def test_only_saves_items_when_necessary(self):
        self.client.get('/')
        self.assertEqual(Team.objects.count(), 0)

    def test_displays_all_teams(self):
        Team.objects.create(name="team 1")
        Team.objects.create(name="team 2")

        response = self.client.get("/")

        self.assertIn("team 1", response.content.decode())
        self.assertIn("team 2", response.content.decode())


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
