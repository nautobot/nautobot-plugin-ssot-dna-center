"""Nautobot SSoT for Cisco DNA Center Adapter for DNA Center SSoT plugin."""

from diffsync import DiffSync


class DnaCenterAdapter(DiffSync):
    """DiffSync adapter for DNA Center."""

    top_level = []

    def __init__(self, *args, job=None, sync=None, client=None, **kwargs):
        """Initialize DNA Center.

        Args:
            job (object, optional): DNA Center job. Defaults to None.
            sync (object, optional): DNA Center DiffSync. Defaults to None.
            client (object): DNA Center API client connection object.
        """
        super().__init__(*args, **kwargs)
        self.job = job
        self.sync = sync
        self.conn = client

    def load(self):
        """Load data from DNA Center into DiffSync models."""
        raise NotImplementedError
