import sys
import os
import unittest
from unittest.mock import patch

# Add the project root to the path to allow importing 'run'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from run import parse_arguments

class TestParseArguments(unittest.TestCase):

    def test_default_arguments(self):
        """
        Tests that the parser returns the correct default values
        when no arguments are given.
        """
        with patch('sys.argv', ['run.py']):
            args = parse_arguments()
            self.assertEqual(args.config, None)
            self.assertEqual(args.output, None)
            self.assertEqual(args.min_score, 0.0)
            self.assertFalse(args.no_odds_mode)
            self.assertEqual(args.min_field_size, 1)
            self.assertEqual(args.max_field_size, None)
            self.assertEqual(args.sort_by, 'score')
            self.assertEqual(args.limit, 10)

    def test_custom_arguments(self):
        """
        Tests that the parser correctly handles custom command-line arguments.
        """
        test_args = [
            'run.py',
            '--config', 'my_config.yaml',
            '--output', 'results.json',
            '--min-score', '5.0',
            '--no-odds-mode',
            '--min-field-size', '5',
            '--max-field-size', '12',
            '--sort-by', 'field_size',
            '--limit', '20'
        ]
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.config, 'my_config.yaml')
            self.assertEqual(args.output, 'results.json')
            self.assertEqual(args.min_score, 5.0)
            self.assertTrue(args.no_odds_mode)
            self.assertEqual(args.min_field_size, 5)
            self.assertEqual(args.max_field_size, 12)
            self.assertEqual(args.sort_by, 'field_size')
            self.assertEqual(args.limit, 20)

if __name__ == '__main__':
    unittest.main()
