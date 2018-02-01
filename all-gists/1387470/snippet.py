"""Simple TCP server for playing Tic-Tac-Toe game.

Use Player-to-Player game mode based on naming auth. 
No thoughts about distribution or pub/sub mode 
(for monitoring or something like this). Just 
basic functionality.
"""

import time
import logging
import signal
import socket

from tornado import stack_context
from tornado.options import options, parse_command_line, define
from tornado.netutil import TCPServer
from tornado.ioloop import IOLoop
from tornado.util import b, bytes_type


class Game(object):
    """Single game representation"""

    UNUSED_CELL = 0

    class Winner(Exception):
        """Control exception for working with game end"""
        def __init__(self, name):
            self.name = name
            super(Game.Winner, self).__init__('Winner!')

    class Draw(Exception):
        """Control exception for working with game end"""
        def __init__(self):
            super(Game.Draw, self).__init__('Draw!')

    # Current state of map
    map = None
    
    # List of possible steps of user 
    allowed_steps = dict([
        ('X', 1),
        ('O', -1)
    ])
    
    def __init__(self, *players, **params):
        self.players = dict(zip(self.allowed_steps.keys(), players))
        self.params = params
        logging.debug('Create game with params: %s', params)
        self.first = 'X'
        self._generate_map()

    def step(self, sign, pos):
        # Check allowed sign
        try:
            val = self.allowed_steps[sign]
        except KeyError:
            raise ValueError('Unknown step sign is given')

        # Check map position 
        # We should make step with using 1-based numeration (not zero-based)
        try:
            if self.map[pos[0]-1][pos[1]-1] != Game.UNUSED_CELL:
                raise ValueError('Position is already in use')
        except IndexError:
            raise ValueError('Illegal position for step')

        # Make step
        self.map[pos[0]-1][pos[1]-1] = val

        # Recalculate game state: 
        # Check if some player is winner on no other step is possible
        limit = self.params.get('win_limit', 3)
        for i, row in enumerate(self.map):
            if abs(sum(row)) == limit:
                raise Game.Winner(self.players[sign].name)

            if abs(sum([r[i] for r in self.map])) == limit:
                raise Game.Winner(self.players[sign].name)

        # Check all possible diagonals 
        up = len(self.map) + 1 - limit
        for s in range(up):
            if any([
                (abs(sum([self.map[i+s][i+s] for i in range(limit)])) == limit),
                (abs(sum([self.map[len(self.map) - (i+1+s)][i+s] for i in range(limit)])) == limit)                             
            ]):
                raise Game.Winner(self.players[sign].name)
        
        if sum([sum(map(abs, r)) for r in self.map]) == len(self.map)**2:
            raise Game.Draw()

    def render(self):
        """Return string of current state map representation"""
        signs = dict([(v,s) for s,v in self.allowed_steps.items()])
        return '\n'.join(map(
            lambda r: ' '.join(map(lambda s: signs.get(s, '.'), r)), 
            self.map
        ))

    def _generate_map(self):
        assert self.map is None, "You couldn't regenerate map"
        size = self.params.get('map_size', 3)
        self.map = [[Game.UNUSED_CELL]*size for i in range(size)]
        logging.debug('Generated map: %s', self.map)
    

class GameSessionMixin(object):
    """Handler of two-players interacion within game"""

    waiter = None

    def join(self):
        """Logic of joining to game session"""
        # Check if there is at least one open game 
        # Connect to game if exist 
        if GameSessionMixin.waiter is not None:
            enemy = GameSessionMixin.waiter
            GameSessionMixin.run(enemy, self)
            GameSessionMixin.waiter = None
        else:
            # Create new one and wait for new connections
            GameSessionMixin.waiter = self
            self.notify('Waiting for incoming player...')

    @staticmethod
    def run(*players):
        """Create game object and choose first runner"""
        game = Game(*players, 
                    map_size=options.map_size, win_limit=options.win_limit)
        message = 'Game is starting. First step by %s.' % game.players[game.first]
        for sign, p in game.players.iteritems():
            p.game = game
            p.sign = sign
            if sign == game.first:
                action = p.make_step
            else:
                action = p.wait_step
            p.notify(message, callback=action)

    def notify(self, note, callback=None):
        """Send game notifications"""
        self.stream.write('%s, %s\n' % (self.name, note), callback=callback)

    def make_step(self):
        self.notify('make your step:', callback=self._on_make_step)

    def _on_make_step(self):
        """Called when make step notification is send"""
        self.stream.read_until(b("\n"), callback=self._on_step)

    def _on_step(self, line):
        """Receive step from user"""
        step = map(int, line.strip().split())
        try:
            self.game.step(self.sign, step)
        except ValueError, e:
            # Cycle for receiving normal step from user 
            self.notify(str(e), callback=self.make_step)
        except Game.Winner, e:
            GameSessionMixin.broadcast(self.game.players.values(),
                                       '%s is WINNER!' % e.name,
                                       'close') 
        except Game.Draw:
            GameSessionMixin.broadcast(self.game.players.values(), 
                                       'DRAW in game!', 
                                       'close') 
        else:
            battle = self.game.render() + '\n'
            for sign, p in self.game.players.iteritems():
                p.stream.write(battle, 
                    callback=(p.wait_step if sign == self.sign else p.make_step))

    def wait_step(self):
        """Just wait for step from other player.

        Of course, we can notify user about this, but it will 
        complicate whole process, cause we will have problems 
        with handling async write operation.
        """
        pass
        
    def close(self):
        """Close players' stream"""
        self.stream.write('Game over\n', callback=self.stream.close)

    @staticmethod
    def broadcast(sub, notification, callback_method):
        """Send notification to each player in ``sub`` list"""
        for s in sub:
            s.notify(notification.strip()+'\n', 
                     callback=s.__getattribute__(callback_method))


class AuthMixin(object):
    """Batch of function for checking auth and registering users"""

    # List of connected players
    # TODO: Add periodic callback for checking player timeout    
    players = set()

    def register(self, on_register=None):
        """Register player with using text name"""
        if on_register:
            self._register_callback = stack_context.wrap(on_register)
        else: 
            self._register_callback = None
        self.stream.write('Enter your name: ', callback=self._on_greeting)

    def _on_greeting(self):
        logging.debug('On greetings call')
        self.stream.read_until(b("\n"), self._on_name)

    def _on_name(self, line):
        """Ask user about name and save it in list of users"""
        logging.debug('On name call with: %s', line)
        name = line.strip()
        if name not in self.__class__.players:
            self.name = name
            self.__class__.players.add(self)
            if self._register_callback:
                self._register_callback()
        else:
            message = 'Name %s is already in used. Choose another one:' % name
            self.stream.write(message, callback=self._on_greeting)

    def unregister(self):
        """Remove player from list of players"""
        try:
            self.__class__.players.remove(str(self))
        except KeyError:
            logging.warning('Try to remove illegal or undefined user')
    

class PlayerConnection(GameSessionMixin, AuthMixin):
    """Player logic handler"""

    # Player's name. Should be setted for auth.
    name = None

    def __init__(self, stream, address, server):
        """Initialize base params and call stream reader for next line"""
        self.stream = stream
        if self.stream.socket.family not in (socket.AF_INET, socket.AF_INET6):
            # Unix (or other) socket; fake the remote address
            address = ('0.0.0.0', 0)
        self.address = address
        self.server = server
        self.stream.set_close_callback(self._on_disconnect)
        
        # Will block current stream flow until user's name is set
        self.register(on_register=self.play)

    def play(self):
        """Main logic function"""
        self.join()        

    def _on_read(self, line):
        """Called when new line received from connection"""
        # Some game logic (or magic)
        self.wait()

    def wait(self):
        """Read from stream until the next signed end of line"""
        self.stream.read_until(b("\n"), self._on_read)

    def _on_disconnect(self, *args, **kwargs):
        """Called on client disconnected"""
        logging.info('Client disconnected %r', self.address)
        # TODO: Should also check current game state and/or waiters status
        self.unregister()

    def __str__(self):
        """Build string representation, will be used for working with
        server identity (not only name) in future"""
        return str(self.name)
        

class TTTServer(TCPServer):
    """TCP server for handling incoming connections from players"""

    def handle_stream(self, stream, address):
        """Called when new IOStream object is ready for usage"""
        logging.info('Incoming connection from %r', address)
        PlayerConnection(stream, address, server=self)

def sig_handler(sig, frame):
    """Catch signal and init callback.
    
    More information about signal processing for graceful stoping 
    Tornado server you can find here:
    http://codemehanika.org/blog/2011-10-28-graceful-stop-tornado.html    
    """
    logging.warning('Caught signal: %s', sig)
    IOLoop.instance().add_callback(shutdown)

def shutdown(): 
    """Stop server and add callback to stop i/o loop"""
    io_loop = IOLoop.instance()

    logging.info('Stopping Tic-Tac-Toe tcp server')
    io_loop.ttt.stop()

    logging.info('Will shutdown in 2 seconds ...')
    io_loop.add_timeout(time.time() + 2, io_loop.stop)

def main():
    """Main processing function"""
    io_loop = IOLoop.instance()

    # Create instance of Tic-Tac-Toe TCP server and save 
    # it as attribute of IOLoop instance. Of course, this 
    # is not the best way to spread ttt instance among 
    # several functions, but it's enough for demo app.
    io_loop.ttt = TTTServer()
    io_loop.ttt.listen(options.port)

    # Init signals handler for TERM and INT signals 
    # (and so KeyboardInterrupt)
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    logging.info('Starting TTT server on %d port', options.port)
    io_loop.start()

define('debug', default=True, type=bool)
define('port', help='Port to listen to', default=8046, type=int)
define('map_size', help='Game map size', default=3, type=int)
define('win_limit', help='Signs to win', default=3, type=int)

if __name__ == '__main__':
    parse_command_line()
    main()