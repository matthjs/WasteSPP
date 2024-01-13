import unittest

from componentannotator.componentannotator import ComponentAnnotator


class TestComponentAnnotator(unittest.TestCase):
    def setUp(self):
        self.component_annotator = ComponentAnnotator("java")

    # Could also use more mocking
    def test_annotate_project(self):
        df_res = self.component_annotator.annotate_project(
            "Aladyn", "https://github.com/NicolasR/Aladyn.git")

        self.assertIsNotNone(df_res)
        exp_columns =  ['path', 'package', 'distribution', 'unannotated', 'label', 'component', 'componentlabel']
        for column in exp_columns:
            self.assertIn(column, df_res.columns)


if __name__ == '__main__':
    unittest.main()
