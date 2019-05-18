#!/usr/bin/env python3
import time

from selenium import webdriver
import unittest

from selenium.webdriver.common.keys import Keys


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        pass
        # self.browser.quit()

    def test_can_create_a_team_and_add_players(self):
        # Edith has heard about a cool new online to-do app. She goes
        # to check out its homepage
        self.browser.get('http://localhost:8000')

        # She notices the page title and header mention Team Manager
        self.assertIn('Team Manager', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Team Manager', header_text)

        # She is invited to create a team straight away
        inputbox = self.browser.find_element_by_id('id_new_team')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a team name'
        )

        # She types "Grey Wolves" into a text box)
        inputbox.send_keys('Grey Wolves')

        # When she hits enter, the page updates, and now the page lists
        # "Grey Wolves" as an item in a list
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(row.text == 'Grey Wolves' for row in rows),
            'New team did not appear in the output rows'
        )
        self.assertTrue(len(rows) == 1)

        # Now there is a place for her to click and add new players to the team
        self.fail('Finish the test!')

        # She is invited to create a new team straight away
#        [...rest of comments as before]

if __name__ == '__main__':
    unittest.main(warnings='ignore')
