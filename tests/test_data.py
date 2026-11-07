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
                self.assertTrue(meal['lizaPortion'])

    def test_nutrition_belongs_to_liza(self):
        self.assertEqual(DATA['nutritionProfile'], 'liza')
        self.assertEqual(DATA['days'][0]['kcal'], 1499)
        self.assertEqual(DATA['days'][0]['macros'], [104, 33, 196])
        self.assertEqual(DATA['days'][29]['macros'], [96, 46, 176])
        breakfast = DATA['days'][0]['meals'][0]
        self.assertIn('хлопья 35 г', breakfast['lizaPortion'])
        self.assertEqual(breakfast['katya'], 'Творожок, бутерброд с яйцом, яблоко')
        self.assertIn('десерт мармелад 15 г', DATA['days'][0]['meals'][3]['lizaPortion'])
        self.assertIn('скумбрия 85 г', DATA['days'][18]['meals'][3]['lizaPortion'])
        self.assertIn('кофе с 50 мл молока', ' '.join(DATA['guidance']).lower())

    def test_updated_shopping_quantities(self):
        pantry = [i['text'] for g in DATA['trips'][0]['groups'] for i in g['items']]
        self.assertIn('спиральки 1,2 кг', pantry)
        self.assertIn('тунец 1705 г без заливки', pantry)
        self.assertIn('печенье 325 г', pantry)
        last = [i['text'] for g in DATA['trips'][9]['groups'] for i in g['items']]
        self.assertIn('сырой картофель 875 г', last)

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
