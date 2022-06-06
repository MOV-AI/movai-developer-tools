import unittest
import mock
from movai_developer_tools.movros.handler import handle as movros_handle
import argparse


argeparse_executor_movros_expose_network_cmd = argparse.Namespace(
    command="does-not-exist"
)


class TestHandler(unittest.TestCase):
    """Handler for unittest"""

    @mock.patch(
        "movai_developer_tools.movros.expose_network.operation_executer.ExposeNetwork.execute"
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argeparse_executor_movros_expose_network_cmd,
    )
    def test_movros_handler_executer_forward(self, mock_argparse, mock_run_executor):
        with self.assertRaises(SystemExit) as se:
            movros_handle()
        self.assertEqual(se.exception.code, 1)
        mock_run_executor.assert_not_called()
