import unittest
import pandas as pd
from io import StringIO

import config
import main


class TestDuplicateDetection(unittest.TestCase):

    def setUp(self):
        self.data = StringIO("""\
contactID,name,name1,email,postalCode,address
1001,C,F,mollis.lectus.pede@outlook.net,39746,449-6990 Tellus. Rd.
1002,C,French,mollis.lectus.pede@outlook.net,39746,123 Elm Street
1003,Ciara,F,non.lacinia.at@zoho.ca,39746,456 Oak St
1004,C,French,mollis.lectus.pede@outlook.net,39746,123 Elm Street
""")
        self.df = pd.read_csv(self.data)

    def test_low_score(self):
        first_contact = self.df.iloc[0].to_dict()
        second_contact = self.df.iloc[2].to_dict()
        score = main.calculate_score(first_contact, second_contact)
        self.assertLess(score, config.POTENTIAL_DUPLICATES_LOW_THREASHOLD)

    def test_medium_score(self):
        first_contact = self.df.iloc[0].to_dict()
        second_contact = self.df.iloc[1].to_dict()
        score = main.calculate_score(first_contact, second_contact)
        self.assertGreater(score, config.POTENTIAL_DUPLICATES_LOW_THREASHOLD)
        self.assertLess(score, config.POTENTIAL_DUPLICATES_HIGH_THREASHOLD)

    def test_high_score(self):
        first_contact = self.df.iloc[1].to_dict()
        second_contact = self.df.iloc[3].to_dict()
        score = main.calculate_score(first_contact, second_contact)
        self.assertGreater(score, config.POTENTIAL_DUPLICATES_HIGH_THREASHOLD)

    def test_find_potential_duplicates(self):
        duplicates_df = main.find_potential_duplicates(self.df)
        self.assertEqual(len(duplicates_df), 3)

    def test_main(self):
        input_file = "test_contacts.xlsx"
        output_file = "test_potential_duplicates.xlsx"

        self.df.to_excel(input_file, index=False)
        main.main(input_file, output_file)

        result_df = pd.read_excel(output_file)
        self.assertGreater(len(result_df), 0)

if __name__ == "__main__":
    unittest.main()