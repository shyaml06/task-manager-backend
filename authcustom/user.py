class CustomUser:
    """
    Lightweight user object for DRF
    (no ORM)
    """

    def __init__(self, user_id, username, role=None,session_id=None):
        self.id = user_id
        self.username = username
        self.role = role
        self.session_id = session_id

    @property
    def is_authenticated(self):
        return True
