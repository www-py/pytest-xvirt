from pathlib import Path
from pytest import Config


class XVirt:
    config: Config

    def virtual_path(self) -> str:
        """Returns the path to be ignored locally and executed remotely."""
        raise NotImplementedError()

    def run(self):
        """
        Should fire the remote execution of the tests and setup the
        infrastructure to receive the events from the remote.
        """
        pass

    def recv_event(self) -> str:
        """Returns the next event received from the remote pytest."""
        pass

    def finalize(self):
        """Finalize the remote execution."""
        pass

    def remote_invocation_params(self, remote_root: str) -> (str, str):
        idir = self.config.invocation_dir
        rp = self.config.rootpath
        rr = remote_root
        invocation_dir = path_rewrite(idir, rp, rr)
        args = [path_rewrite(a, rp, rr) for a in self.config.args]
        return invocation_dir, args


def path_rewrite(invocation_dir, root_path: Path, remote_root: str) -> str:
    root_path_str = str(root_path)
    return str(invocation_dir).replace(root_path_str, remote_root)
