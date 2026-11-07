import json
import unittest
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / 'data.json').read_text())

class MenuDataTest(unittest.TestCase):
    def test_complete_month_and_profiles(self):
        self.assertEqual([d['day'] for d in DATA['days']], list(range(1, 31)))
        for day in DATA['days']:
            self.assertEqual(len(day['meals']), 4)
            self.assertEqual(len(day['macros']), 3)
            for meal in day['meals']:
                self.assertTrue(meal['katya'])
                self.assertTrue(meal['liza'])

    def test_source_specific_differences(self):
        self.assertIn('сельдью', DATA['days'][11]['meals'][3]['liza'])
        self.assertIn('Рис с яйцом', DATA['days'][11]['meals'][3]['katya'])
        self.assertIn('скумбрией', DATA['days'][18]['meals'][3]['liza'])
        self.assertIn('тунцом', DATA['days'][18]['meals'][3]['katya'])
        self.assertIn('крабовыми', DATA['days'][25]['meals'][3]['liza'])

    def test_shopping_and_prep(self):
        self.assertEqual(len(DATA['trips']), 10)
        items = [i for t in DATA['trips'] for g in t['groups'] for i in g['items']]
        self.assertEqual(len(items), 227)
        self.assertEqual(len({i['id'] for i in items}), 227)
        self.assertEqual([p['day'] for p in DATA['prep']], [0,3,7,10,14,17,21,24,28])
        self.assertEqual(len(DATA['recipes']), 25)
        titles = {r['title'] for r in DATA['recipes']}
        for p in DATA['prep']:
            for food in p['foods']:
                self.assertIn(food, titles)
