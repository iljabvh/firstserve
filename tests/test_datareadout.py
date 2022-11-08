import unittest
from pandas import read_csv

"""
Testing file importing:
- csv data files with unintuitive formatting, make sure to provide a test.csv file yourself, 
it should have the format like the main file/s: wta.csv, atp.csv

"""


class TestCSVImport(unittest.TestCase):
    def test_count_rows(self):

        """
        count rows of both dictionary and dataframe, make sure that no weird formatting issues have arisen
        :return: comparison between df and dict
        """

        testdb_path = f'./testdata/test_matches.csv'
        db_dict = read_csv(testdb_path).to_dict()
        db_df = read_csv(testdb_path)

        df_col_number = len(db_df.columns)
        dict_keys_number = len(db_dict.keys())

        df_row_number = len(db_df)

        self.assertIn('ID', db_dict.keys())

        dict_item_number = len(db_dict['ID'])

        self.assertEqual(dict_keys_number, df_col_number)
        self.assertEqual(dict_item_number, df_row_number)


if __name__ == '__main__':
    unittest.main()
