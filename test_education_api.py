import unittest
from unittest.mock import patch, MagicMock
import json
from education import EducationAPI

class TestEducationAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api = EducationAPI()
        
        # Sample response data for mocking
        self.sample_public_schools = {
            'features': [
                {
                    'properties': {
                        'NAME': 'Test Public School',
                        'ZIPCODE': '33101',
                        'ADDRESS': '123 Test St',
                        'CITY': 'Miami',
                        'SCHOOL_ID': 'PS001'
                    }
                }
            ]
        }
        
        self.sample_private_schools = {
            'features': [
                {
                    'properties': {
                        'NAME': 'Test Private School',
                        'ZIPCODE': '33101',
                        'ADDRESS': '456 Test Ave',
                        'CITY': 'Miami',
                        'SCHOOL_ID': 'PR001'
                    }
                }
            ]
        }
        
        self.sample_school_ratings = {
            'features': [
                {
                    'properties': {
                        'SCHOOL_ID': 'PS001',
                        'RATING': 'A',
                        'SCORE': 95
                    }
                }
            ]
        }
        
        self.sample_bus_stops = {
            'features': [
                {
                    'properties': {
                        'ROUTEID': 'R001',
                        'LOCATION': '33101',
                        'STOP_NAME': 'Test Stop'
                    }
                }
            ]
        }

    @patch('education.EducationAPI.fetch_data_with_retry')
    def test_get_schools_by_zip(self, mock_fetch):
        """Test getting schools by ZIP code."""
        # Mock the API responses
        mock_fetch.side_effect = [
            self.sample_public_schools,
            self.sample_private_schools
        ]
        
        # Test getting all schools
        result = self.api.get_schools_by_zip('33101')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['schools']), 2)
        
        # Test getting only public schools
        result = self.api.get_schools_by_zip('33101', school_type='public')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['schools']), 1)
        self.assertEqual(result['data']['schools'][0]['school_type'], 'public')
        
        # Test getting only private schools
        result = self.api.get_schools_by_zip('33101', school_type='private')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['schools']), 1)
        self.assertEqual(result['data']['schools'][0]['school_type'], 'private')

    @patch('education.EducationAPI.fetch_data_with_retry')
    def test_get_school_by_name(self, mock_fetch):
        """Test searching for schools by name."""
        # Mock the API responses
        mock_fetch.side_effect = [
            self.sample_public_schools,
            self.sample_private_schools
        ]
        
        # Test searching for existing school
        result = self.api.get_school_by_name('Test')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['schools']), 2)
        
        # Test searching for non-existent school
        result = self.api.get_school_by_name('Nonexistent')
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'NOT_FOUND')

    @patch('education.EducationAPI.fetch_data_with_retry')
    def test_get_bus_stops_by_zip(self, mock_fetch):
        """Test getting bus stops by ZIP code."""
        # Mock the API response
        mock_fetch.return_value = self.sample_bus_stops
        
        # Test getting bus stops
        result = self.api.get_bus_stops_by_zip('33101')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['bus_stops']), 1)

    @patch('education.EducationAPI.fetch_data_with_retry')
    def test_get_bus_stops_by_route(self, mock_fetch):
        """Test getting bus stops by route."""
        # Mock the API response
        mock_fetch.return_value = self.sample_bus_stops
        
        # Test getting bus stops for existing route
        result = self.api.get_bus_stops_by_route('R001')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']['bus_stops']), 1)
        
        # Test getting bus stops for non-existent route
        result = self.api.get_bus_stops_by_route('R999')
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'NOT_FOUND')

    @patch('education.EducationAPI.fetch_data_with_retry')
    def test_get_school_ratings(self, mock_fetch):
        """Test getting school ratings."""
        # Mock the API response
        mock_fetch.return_value = self.sample_school_ratings
        
        # Test getting ratings for existing school
        result = self.api.get_school_ratings('PS001')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['ratings']['RATING'], 'A')
        
        # Test getting ratings for non-existent school
        result = self.api.get_school_ratings('PS999')
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'NOT_FOUND')

    def test_error_handling(self):
        """Test error handling in API calls."""
        # Test with invalid ZIP code
        result = self.api.get_schools_by_zip('invalid')
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'PROCESSING_ERROR')
        
        # Test with invalid school name
        result = self.api.get_school_by_name('')
        self.assertFalse(result['success'])
        self.assertEqual(result['error_code'], 'PROCESSING_ERROR')

if __name__ == '__main__':
    unittest.main() 