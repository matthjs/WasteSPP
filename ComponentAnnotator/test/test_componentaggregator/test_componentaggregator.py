import unittest
from unittest.mock import patch, Mock
import pandas as pd
from componentaggregator.componentaggregator import ComponentAggregator

def dummy_component_annot_df():
    columns = ['path', 'package', 'distribution', 'unannotated', 'label', 'component', 'componentlabel']

    data = {
        'path': ['/file1', '/file2', '/file3'],
        'package': ['pkg1', 'pkg2', 'pkg3'],
        'distribution': ['dist1', 'dist2', 'dist3'],
        'unannotated': [True, False, True],
        'label': ['Label1', 'Label2', 'Label3'],
        'component': [1, 2, 1],
        'componentlabel': ['CompLabel1', 'CompLabel2', 'CompLabel1']
    }

    return pd.DataFrame(data, columns=columns)

class TestComponentAggregator(unittest.TestCase):

    def setUp(self):
        self.component_aggregator = ComponentAggregator()


    def test_database(self):
        db_engine = self.component_aggregator.engine
        self.assertIsNotNone(db_engine)

        df_dummy1 = dummy_component_annot_df()
        df_dummy2 = dummy_component_annot_df()

        df_dummy1.to_sql("test1", db_engine, if_exists='replace', index=False)
        df_dummy2.to_sql("test2", db_engine, if_exists='replace', index=False)

        df_dummy1_retr = pd.read_sql("test1", db_engine)
        df_dummy2_retr = pd.read_sql("test2", db_engine)

        self.assertIsNotNone(df_dummy1_retr)
        self.assertTrue(df_dummy1_retr.equals(df_dummy1))

        self.assertIsNotNone(df_dummy2_retr)
        self.assertTrue(df_dummy2_retr.equals(df_dummy2))


if __name__ == '__main__':
    unittest.main()
