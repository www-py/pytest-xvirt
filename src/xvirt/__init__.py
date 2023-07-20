class XVirt:

    def remote_path(self) -> str:
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
