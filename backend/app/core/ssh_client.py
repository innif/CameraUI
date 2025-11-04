"""SSH client for executing remote system commands"""
import logging
import paramiko
from typing import Tuple, Optional
from .config import settings


logger = logging.getLogger(__name__)


class SSHClient:
    """Helper class for SSH connections and command execution"""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key_file: Optional[str] = None
    ):
        """
        Initialize SSH client with connection parameters

        Args:
            host: SSH host (defaults to settings.ssh_host, which uses OBS_HOST if SSH_HOST is empty)
            port: SSH port (defaults to settings.SSH_PORT)
            username: SSH username (defaults to settings.SSH_USERNAME)
            password: SSH password (defaults to settings.SSH_PASSWORD)
            key_file: Path to SSH private key file (defaults to settings.SSH_KEY_FILE)
        """
        self.host = host or settings.ssh_host
        self.port = port or settings.SSH_PORT
        self.username = username or settings.SSH_USERNAME
        self.password = password or settings.SSH_PASSWORD
        self.key_file = key_file or settings.SSH_KEY_FILE

    def execute_command(self, command: str, timeout: int = 10) -> Tuple[bool, str, str]:
        """
        Execute a command via SSH

        Args:
            command: Command to execute
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr)
        """
        client = None
        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": timeout
            }

            # Use key file if specified, otherwise use password
            if self.key_file:
                connect_kwargs["key_filename"] = self.key_file
            elif self.password:
                connect_kwargs["password"] = self.password
            else:
                raise ValueError("Either SSH password or key file must be provided")

            logger.info(f"Connecting to {self.username}@{self.host}:{self.port}")
            client.connect(**connect_kwargs)

            # Execute command
            logger.info(f"Executing command: {command}")
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)

            # Get output
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()

            success = exit_code == 0

            if success:
                logger.info(f"Command executed successfully")
            else:
                logger.error(f"Command failed with exit code {exit_code}: {stderr_text}")

            return success, stdout_text, stderr_text

        except Exception as e:
            error_msg = f"SSH command execution failed: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

        finally:
            if client:
                client.close()

    def shutdown(self) -> Tuple[bool, str]:
        """
        Shutdown the remote system

        Returns:
            Tuple of (success, message)
        """
        logger.warning(f"Initiating shutdown of {self.host}")
        success, stdout, stderr = self.execute_command("sudo shutdown -h now", timeout=5)

        if success or "shutdown" in stdout.lower() or "shutdown" in stderr.lower():
            # Even if we get a connection error, shutdown might have worked
            message = "System shutdown initiated successfully"
            logger.info(message)
            return True, message
        else:
            message = f"Failed to shutdown system: {stderr or stdout}"
            logger.error(message)
            return False, message

    def reboot(self) -> Tuple[bool, str]:
        """
        Reboot the remote system

        Returns:
            Tuple of (success, message)
        """
        logger.warning(f"Initiating reboot of {self.host}")
        success, stdout, stderr = self.execute_command("sudo reboot", timeout=5)

        if success or "reboot" in stdout.lower() or "reboot" in stderr.lower():
            # Even if we get a connection error, reboot might have worked
            message = "System reboot initiated successfully"
            logger.info(message)
            return True, message
        else:
            message = f"Failed to reboot system: {stderr or stdout}"
            logger.error(message)
            return False, message
