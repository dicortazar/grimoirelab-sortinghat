#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import unittest
import unittest.mock

import click.testing

from sortinghat.cli.client import SortingHatClientError
from sortinghat.cli.cmds.enroll import enroll


ENROLL_CMD_OP = """mutation {{
  enroll(
      uuid: "{}"
      group: "{}"
      fromDate: "{}"
      toDate: "{}"
      force: {}
    ) {{
    uuid
  }}
}}"""

ENROLL_DEFAULT_CMD_OP = """mutation {{
  enroll(uuid: "{}", group: "{}", force: {}) {{
    uuid
  }}
}}"""


ENROLL_NOT_FOUND_ERROR = (
    "FFFFFFFFFFFFFFF not found in the registry"
)

ENROLL_INVALID_DATE_ERROR = (
    "{} is not a valid date"
)


class MockClient:
    """Mock client"""

    def __init__(self, responses):
        self.responses = responses
        self.ops = []

    def connect(self):
        pass

    def disconnect(self):
        pass

    def execute(self, operation):
        self.ops.append(operation)
        response = self.responses.pop(0)

        if isinstance(response, SortingHatClientError):
            raise response
        else:
            return response


class TestEnrollCommand(unittest.TestCase):
    """Enroll command unit tests"""

    @unittest.mock.patch('sortinghat.cli.utils.SortingHatClient')
    def test_enroll(self, mock_client):
        """Check if it creates a new enrollment"""

        responses = [
            {'data': {'enroll': {'uuid': '322397ed782a798ffd9d0bc7e293df4292fe075d'}}}
        ]
        client = MockClient(responses)
        mock_client.return_value = client

        runner = click.testing.CliRunner()

        # Create a new enrollment
        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'Example',
            '--from-date', '2012-01-01',
            '--to-date', '2013-01-01',
        ]
        result = runner.invoke(enroll, params)

        expected = ENROLL_CMD_OP.format('322397ed782a798ffd9d0bc7e293df4292fe075d',
                                        'Example',
                                        '2012-01-01T00:00:00+00:00',
                                        '2013-01-01T00:00:00+00:00',
                                        'false')
        self.assertEqual(len(client.ops), 1)
        self.assertEqual(str(client.ops[0]), expected)

        self.assertEqual(result.exit_code, 0)

    @unittest.mock.patch('sortinghat.cli.utils.SortingHatClient')
    def test_enroll_default_dates(self, mock_client):
        """Check if it creates a new enrollment with default dates"""

        responses = [
            {'data': {'enroll': {'uuid': '322397ed782a798ffd9d0bc7e293df4292fe075d'}}}
        ]
        client = MockClient(responses)
        mock_client.return_value = client

        runner = click.testing.CliRunner()

        # Create a new enrollment
        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'Example'
        ]
        result = runner.invoke(enroll, params)

        expected = ENROLL_DEFAULT_CMD_OP.format('322397ed782a798ffd9d0bc7e293df4292fe075d',
                                                'Example',
                                                'false')
        self.assertEqual(len(client.ops), 1)
        self.assertEqual(str(client.ops[0]), expected)

        self.assertEqual(result.exit_code, 0)

    @unittest.mock.patch('sortinghat.cli.utils.SortingHatClient')
    def test_enroll_force(self, mock_client):
        """Check if force flag is set"""

        responses = [
            {'data': {'enroll': {'uuid': '322397ed782a798ffd9d0bc7e293df4292fe075d'}}}
        ]
        client = MockClient(responses)
        mock_client.return_value = client

        runner = click.testing.CliRunner()

        # Create a new enrollment
        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'Example',
            '--from-date', '2012-01-01',
            '--to-date', '2013-01-01',
            '--force'
        ]
        result = runner.invoke(enroll, params)

        expected = ENROLL_CMD_OP.format('322397ed782a798ffd9d0bc7e293df4292fe075d',
                                        'Example',
                                        '2012-01-01T00:00:00+00:00',
                                        '2013-01-01T00:00:00+00:00',
                                        'true')
        self.assertEqual(len(client.ops), 1)
        self.assertEqual(str(client.ops[0]), expected)

        self.assertEqual(result.exit_code, 0)

    @unittest.mock.patch('sortinghat.cli.utils.SortingHatClient')
    def test_invalid_dates_error(self, mock_client):
        """"Check if it fails when an invalid date is given"""

        client = MockClient([])
        mock_client.return_value = client

        runner = click.testing.CliRunner(mix_stderr=False)

        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'Example',
            '--from-date', '2011-13-01'
        ]
        result = runner.invoke(enroll, params)

        self.assertEqual(len(client.ops), 0)

        expected_err = "Error: " + ENROLL_INVALID_DATE_ERROR.format('2011-13-01') + '\n'
        self.assertEqual(result.stderr, expected_err)
        self.assertEqual(result.exit_code, 1)

        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'Example',
            '--to-date', 'AAAAAA'
        ]
        result = runner.invoke(enroll, params)

        self.assertEqual(len(client.ops), 0)

        expected_err = "Error: " + ENROLL_INVALID_DATE_ERROR.format('AAAAAA') + '\n'
        self.assertEqual(result.stderr, expected_err)
        self.assertEqual(result.exit_code, 1)

    @unittest.mock.patch('sortinghat.cli.utils.SortingHatClient')
    def test_error(self, mock_client):
        """"Check if it fails when an error is sent by the server"""

        error = {
            'message': ENROLL_NOT_FOUND_ERROR,
            'extensions': {
                'code': 9
            }
        }

        responses = [
            SortingHatClientError(error['message'], errors=[error])
        ]
        client = MockClient(responses)
        mock_client.return_value = client

        runner = click.testing.CliRunner(mix_stderr=False)

        params = [
            '322397ed782a798ffd9d0bc7e293df4292fe075d',
            'FFFFFFFFFFFFFFF'
        ]
        result = runner.invoke(enroll, params)

        expected = ENROLL_DEFAULT_CMD_OP.format('322397ed782a798ffd9d0bc7e293df4292fe075d',
                                                'FFFFFFFFFFFFFFF',
                                                'false')
        self.assertEqual(len(client.ops), 1)
        self.assertEqual(str(client.ops[0]), expected)

        expected_err = "Error: " + ENROLL_NOT_FOUND_ERROR + '\n'
        self.assertEqual(result.stderr, expected_err)
        self.assertEqual(result.exit_code, 9)


if __name__ == '__main__':
    unittest.main()
