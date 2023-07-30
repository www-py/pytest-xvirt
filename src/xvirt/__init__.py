class XVirt:

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


def path_rewrite(current_path: str, virtual_path: str, new_path: str) -> str:
    return current_path.replace(virtual_path, new_path)
