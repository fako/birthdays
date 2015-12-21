from ..person import PersonSource


class SoccerSource(PersonSource):

    def split_full_name(self, force=False):
        super(SoccerSource, self).split_full_name(force=force)
        self.initials = self.first_name if self.first_name is not None and len(self.first_name) <= 20 else None
        self.first_name = None


class BilliardSource(PersonSource):
    pass


class HockeySource(PersonSource):
    pass


class TriathlonSource(PersonSource):
    pass