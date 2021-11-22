class Seat:

    BLOCKS = 5
    ROWS = 2
    PLACES = 3

    def __init__(self, block, row, place):
        self.block = block
        self.row = row
        self.place = place

    def __str__(self):
        return "Block: {}, Row: {}, Place: {}".format(self.block, self.row, self.place)

    @staticmethod
    def get_seats():
        seats = []
        for block in range(1, Seat.BLOCKS + 1):
            for row in range(1, Seat.ROWS + 1):
                for place in range(1, Seat.PLACES + 1):
                    seats.append(Seat(block, row, place))
        return seats