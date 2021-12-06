from db.matchesDB import MatchDB


class MatchDoesNotExistError(Exception):
    pass


class Match:
    def __init__(self, id, host_team, guest_team, date, organizer, match_type):
        if id == None:
            self.id = Match.new_id()
        else:
            self.id = id
        self.host_team = host_team
        self.guest_team = guest_team
        self.date = date
        self.organizer = organizer
        self.match_type = match_type

    def __str__(self):
        return "----- Match {} -----\n{} vs {}\n{} Stage\nDate: {}".format(self.id, self.host_team, self.guest_team, self.match_type, self.date)

    @staticmethod
    def construct(match_id):
        if not MatchDB.does_exist(match_id):
            raise MatchDoesNotExistError()
        row = MatchDB.get_by_id(match_id)
        return Match(row[0], row[1], row[2], row[3], row[4], row[5])

    def save(self):
        MatchDB.update_match(self)
    
    @staticmethod
    def new_id():
        res = MatchDB.get_matches()
        if not res == 0:
            res = [res[i][0] for i in range(len(res))]
            return max(res) + 1
        else:
            return 1