import json
from tempfile import NamedTemporaryFile
import unittest

from taskgen import taskgen

LIST_HEAD_SOURCE = "a <- [int] | b <- head a"


class TestTaskGen(unittest.TestCase):
    def test_stdin(self):
        taskgen.sys.stdin = [LIST_HEAD_SOURCE]
        args = taskgen.parse_args(["--stdin"])
        result = taskgen.main(args)
        self.verify_list_head_result(result)

    def test_from_json(self):
        with NamedTemporaryFile(mode="w+") as f:
            json.dump([{"source": LIST_HEAD_SOURCE}], f)
            f.seek(0)
            args = taskgen.parse_args(["--from-json", f.name])
            result = taskgen.main(args)
            self.verify_list_head_result(result)

    def test_from_txt(self):
        with NamedTemporaryFile(mode="w+") as f:
            f.write(LIST_HEAD_SOURCE)
            f.seek(0)
            args = taskgen.parse_args(["--from-txt", f.name])
            result = taskgen.main(args)
            self.verify_list_head_result(result)

    def verify_list_head_result(self, result):
        assert isinstance(result, list)
        self.assertEqual(len(result), 1)
        assert isinstance(result[0], dict)
        assert "program" in result[0]
        self.assertEqual(result[0]["program"].bounds, [(0, 99)])
        assert "io_pairs" in result[0]
        self.assertEqual(len(result[0]["io_pairs"]), 10)
        assert isinstance(result[0]["io_pairs"][0]["o"], int)


if __name__ == "__main__":
    unittest.main()
