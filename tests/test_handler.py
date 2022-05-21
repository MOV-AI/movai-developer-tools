import unittest
import mock
from movai_developer_tools.movros.handler import handle as movros_handle
import argparse


def mock_add_expected_arguments(parser):
    parser.add_argument("--dummy_arg")


argeparse_executor_movros_expose_network_cmd = argparse.Namespace(
    command="expose-network", workspace="DUMMY_PATH"
)

# argeparse_extra_arg = argparse.Namespace(
#     command="command_operation", workspace="DUMMY_PATH", dummy_arg="test"
# )


# TODO fix the broken tests as soon as you change/delete the dummy executer
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
        movros_handle()
        mock_run_executor.assert_called_with(
            argeparse_executor_movros_expose_network_cmd
        )

    # @mock.patch(
    #     "movai_developer_tools.movros.expose_network.operation_executer.ExposeNetwork.add_expected_arguments",
    #     side_effect=mock_add_expected_arguments,
    # )
    # @mock.patch(
    #     "movai_developer_tools.movros.expose_network.operation_executer.ExposeNetwork.execute"
    # )
    # @mock.patch("argparse.ArgumentParser.parse_args", return_value=argeparse_extra_arg)
    # def test_movros_handler_request_executor_arguments(
    #     self, mock_argparse, mock_run_executor, mock_add_arg
    # ):
    #     movros_handle()

    #     mock_add_arg.assert_called_once()

    #     expected_value = argeparse_extra_arg.dummy_arg
    #     obtained_value = mock_run_executor.call_args.args[0].dummy_arg

    #     self.assertEqual(expected_value, obtained_value)
