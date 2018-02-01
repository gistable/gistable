#!/usr/bin/python


class Toy(object):
    inventory = 0
    
    def __init__(self, price, name, quantity):
        self.price = price
        self.name = name
        self.quantity = quantity
        Toy.inventory += quantity
        
    def __del__(self):
        self._reduce_inventory(self.quantity)
        
    def __repr__(self):
        return "Toy: %s for $%s" % (self.name,
                                    self.price)
                                    
    def _get_base_value(self):
        return float(self.price) * float(self.quantity)
    
    def _reduce_inventory(self, num):
        Toy.inventory -= num
    
    def get_total_value(self):
        """
        Override this function for our software to work
        """
        raise Exception("You must implement get_total_value")
        
    def sell(self, num=1):
        self.quantity -= num
        self._reduce_inventory(num)
        


class ActionFigure(Toy):
    
    def __init__(self, price, name, quantity, royalty_rate):
        super(ActionFigure, self).__init__(price, name, quantity)
        self.royalty_rate = royalty_rate
    
    def get_total_value(self):
        mine = 1 - self.royalty_rate
        return self._get_base_value() * float(mine)
        
    def get_vendor_proceeds(self):      
        return self._get_base_value() * self.royalty_rate
        

class BoardGame(Toy):
    
        def __init__(self, price, name, quantity, players=1):
            super(BoardGame, self).__init__(price, name, quantity)
            self.players = 1
            if players > 0:
                self.players = players
            
        def __repr__(self):
            return "%s ($%s) is meant for %s players" % (self.name,
                                    self.price, self.players)
        
        def price_per_person(self):
            return float(self.price)/float(self.players)

    
def test_action_figure():
    a = ActionFigure(29.00, "Batman", 50, .1)
    assert(a.get_total_value() == 1305.00)
    print a

def test_sell():
    a = ActionFigure(29.00, "Batman", 50, .1)
    a.sell()
    assert(a.get_total_value() == 1278.9)
    print a
    
def test_vendor_proceeds():
    a = ActionFigure(10.00, "Batman", 50, .1)
    assert(a.get_vendor_proceeds() == 50.00)
    print a
    
def test_board_game():
    b = BoardGame(40.00, "Scrabble", 10, 4)
    assert(b.price_per_person() == 10.00)
    print b
    
def test_no_players():
    b = BoardGame(40.00, "Scrabble", 10, 0)
    assert(b.price_per_person() == 40.00)
    print b
    
def test_inventory():
    b = BoardGame(40.00, "Scrabble", 10, 0)
    a1 = ActionFigure(29.00, "Batman", 50, .1)
    a2 = ActionFigure(29.00, "Batman", 100, .1)
    assert(Toy.inventory == 160)


if __name__ == '__main__':
    test_action_figure()
    test_sell()
    test_vendor_proceeds()
    test_board_game()
    test_no_players()
    test_inventory()
