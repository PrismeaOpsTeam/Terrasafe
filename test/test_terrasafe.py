import os
import sys
import unittest
from unittest.mock import patch

from terrasafe import terrasafe


class TerrasafeTest(unittest.TestCase):
    resource_delete = {
        "change": {
            "actions": [
                "delete"
            ]
        }
    }

    resource_recreate = {
        "change": {
            "actions": [
                "delete",
                "create"
            ]
        }
    }

    resource_update = {
        "change": {
            "actions": [
                "update"
            ]
        }
    }

    def setUp(self):
        self.input_file = open('test/test-input.json', 'r')
        sys.stdin = self.input_file

    def tearDown(self):
        self.input_file.close()

    def test_load_config(self):
        config = terrasafe.load_config("./test/test-config.json")
        self.assertListEqual(config["ignore_deletion"],
                             ["aws_ecs_task_definition*", "1"])
        self.assertListEqual(config["ignore_deletion_if_recreation"],
                             ["aws_ecs_task_definition*", "2"])
        self.assertListEqual(config["unauthorized_deletion"],
                             ["aws_ecs_task_definition*", "3"])

    def test_parse_ignored_from_env_var(self):
        os.environ["TERRASAFE_ALLOW_DELETION"] = "a;b;c"
        res = terrasafe.parse_ignored_from_env_var()
        self.assertListEqual(res, ["a", "b", "c"])

    def test_parse_ignored_from_empty_env_var(self):
        os.environ["TERRASAFE_ALLOW_DELETION"] = ""
        res = terrasafe.parse_ignored_from_env_var()
        self.assertListEqual(res, [])

    def test_get_resource_deletion(self):
        all_deletion = terrasafe.get_resource_deletion()
        all_deletion_address = list(map(lambda res: res["address"], all_deletion))
        self.assertListEqual(all_deletion_address, ['aws_s3_bucket.b[0]', 'aws_test.test'])

    def test_has_delete_action(self):
        self.assertTrue(terrasafe.has_delete_action(self.resource_delete))
        self.assertTrue(terrasafe.has_delete_action(self.resource_recreate))
        self.assertFalse(terrasafe.has_delete_action(self.resource_update))

    def test_is_resource_recreate(self):
        self.assertFalse(terrasafe.is_resource_recreate(self.resource_delete))
        self.assertTrue(terrasafe.is_resource_recreate(self.resource_recreate))
        self.assertFalse(terrasafe.is_resource_recreate(self.resource_update))

    def test_is_resource_match_any(self):
        self.assertTrue(terrasafe.is_resource_match_any("ab.cd", ["c", "d", "ab*"]))
        self.assertFalse(terrasafe.is_resource_match_any("ab.cd", ["c", "ab"]))

    def test_is_deletion_commented(self):
        self.assertFalse(terrasafe.is_deletion_commented("test", "test"))
        self.assertFalse(terrasafe.is_deletion_commented("aws_s3_bucket", "b"))
        self.assertFalse(terrasafe.is_deletion_commented("aws_s3_bucket", "other_bucket"))
        self.assertTrue(terrasafe.is_deletion_commented("aws_type", "abc"))
        self.assertTrue(terrasafe.is_deletion_commented("aws_type2", "def"))

    def test_is_deletion_in_disabled_file(self):
        self.assertTrue(terrasafe.is_deletion_in_disabled_file("aws_type3", "disabled"))
        self.assertFalse(terrasafe.is_deletion_in_disabled_file("aws_s3_bucket", "b"))

    def test_all_tf_files(self):
        self.assertCountEqual(terrasafe.get_all_files(".tf"), ["./test/test.tf", "./test/test2.tf"])

    def test_main_fail(self):
        with patch.object(sys, 'argv', ["terrasafe"]), self.assertRaises(SystemExit):
            terrasafe.main()

    def test_main_fail_with_unauthorized(self):
        with patch.object(sys, 'argv', ["terrasafe", "--config", "./test/test-config-unauthorized.json"]), \
             self.assertRaises(SystemExit):
            terrasafe.main()

    def test_main_ok_ignore(self):
        with patch.object(sys, 'argv', ["terrasafe", "--config", "./test/test-config-ignore-all.json"]):
            terrasafe.main()

    def test_main_ok_ignore_with_var(self):
        os.environ["TERRASAFE_ALLOW_DELETION"] = "aws_s3_bucket.b[0];aws_test.*"
        with patch.object(sys, 'argv', ["terrasafe"]):
            terrasafe.main()
