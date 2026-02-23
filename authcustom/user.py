class CustomUser:
    """
    Lightweight user object for DRF
    (no ORM)
    """

    def __init__(self, user_id, username, role=None):
        self.id = user_id
        self.username = username
        self.role = role

    @property
    def is_authenticated(self):
        return True
