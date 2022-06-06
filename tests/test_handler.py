import unittest
import mock
from movai_developer_tools.movros.handler import handle as movros_handle
import argparse


movros_handle_bad_argument = argparse.Namespace(command="does-not-exist")


class TestHandler(unittest.TestCase):
    """Handler for unittest."""

    @mock.patch(
        "movai_developer_tools.movros.expose_network.operation_executer.ExposeNetwork.execute"
    )
    @mock.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=movros_handle_bad_argument,
    )
    def test_movros_handler_bad_argument(
        self, mock_argparse: argparse.Namespace, mock_run_executor
    ) -> None:
        """Test bad argument for movros handle.

        Args:
            mock_argparse: Mock argparse with a bad argument.
            mock_run_executor: Mock the execute function inside the handler.

        """
        with self.assertRaises(SystemExit) as se:
            movros_handle()
        self.assertEqual(se.exception.code, 1)
        mock_run_executor.assert_not_called()
