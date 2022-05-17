import unittest
import mock
from movai_developer_tools.handler import handle
import argparse


def mock_add_expected_arguments(parser):
    parser.add_argument("--dummy_arg")


argeparse_executor_dummy_cmd = argparse.Namespace(
    command="command_operation", workspace="DUMMY_PATH"
)


# TODO fix the broken tests as soon as you change/delete the dummy executer
class TestHandler(unittest.TestCase):
    @mock.patch("movai_developer_tools.setup_ros.operation_executer.SetupRos.execute")
    @mock.patch(
        "argparse.ArgumentParser.parse_args", return_value=argeparse_executor_dummy_cmd
    )
    def test_handler_executer_forward(self, mock_argparse, mock_run_executor):
        handle()
        mock_run_executor.assert_called_with(argeparse_executor_dummy_cmd)

    argeparse_extra_arg = argparse.Namespace(
        command="command_operation", workspace="DUMMY_PATH", dummy_arg="test"
    )

    @mock.patch(
        "movai_developer_tools.setup_ros.operation_executer.SetupRos.add_expected_arguments",
        side_effect=mock_add_expected_arguments,
    )
    @mock.patch("movai_developer_tools.setup_ros.operation_executer.SetupRos.execute")
    @mock.patch("argparse.ArgumentParser.parse_args", return_value=argeparse_extra_arg)
    def test_handler_request_executor_arguments(
        self, mock_argparse, mock_run_executor, mock_add_arg
    ):
        handle()

        mock_add_arg.assert_called_once()

        expected_value = self.argeparse_extra_arg.dummy_arg
        obtained_value = mock_run_executor.call_args.args[0].dummy_arg

        self.assertEqual(expected_value, obtained_value)
