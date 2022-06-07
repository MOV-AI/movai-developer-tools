import unittest
from movai_developer_tools.movros.expose_network.operation_executer import (
    ExposeNetwork,
)


class TestOperationExecutor(unittest.TestCase):
    """Test opertation executors."""

    def test_operation_expose_network(self):
        """Test execution of expose-network command.

        If the test succeeds it will catch the system exit at
        movai_developer_tools.utils.container_tools.ContainerTools.
        """
        with self.assertRaises(SystemExit) as se:
            ExposeNetwork().execute()
        self.assertEqual(se.exception.code, 1)
