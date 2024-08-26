import Pyro5.server
import numpy as np

@Pyro5.server.behavior(instance_mode="single")
class FourLinesServer(object):
    def __init__(self, dimension=7):
        # dimension of the board
        if dimension < 4:
            self._dimension = 4
        else:
            self._dimension = dimension
        
        # game variables
        self._board = np.zeros((dimension,dimension), int) # generate board with zeros
        self._players = []
        self._game_over = False
        self._winner = None
        self._last_move = None
        self._move_count = 0
        self._turn = ''

    @Pyro5.server.expose
    @property
    def board(self):
        """
            Flips the board vertically and returns it as a list of lists.

        Returns:
            list: returns the board as a list of lists, where each list is a row of the board
        """
        return np.flipud(self._board.copy()).tolist()
    
    @Pyro5.server.expose
    @property
    def turn(self):
        return self._turn
    
    @Pyro5.server.expose
    @property
    def players(self):
        return self._players
    
    @Pyro5.server.expose
    @property
    def game_over(self):
        return self._game_over
    
    @Pyro5.server.expose
    @property
    def winner(self):
        return self._winner
    
    @Pyro5.server.expose
    @property
    def dimension(self):
        return self._dimension
    
    @Pyro5.server.expose
    def join_game(self, player):
        if len(self._players) < 2: # check slot availability
            if player in self._players:
                raise ConnectionError('Player already in game')
            else:
                self._players.append(player)
                print(f"Player {player} joined the game")
                if len(self._players) == 2: # start game
                    self._turn = self._players[0]
                    print(f"Player {self._players[0]} turn")
        else:
            raise ConnectionError('Game in progress')
        
    @Pyro5.server.expose
    def leave_game(self, player):
        # if player is in the game, remove it and reset game
        if player in self._players:
            self._game_over = False
            self._winner = None
            self._board = np.zeros((self._dimension,self._dimension), int)
            self._move_count = 0
            self._turn = ''
            
            self._players.remove(player)
            print(f"Player {player} left the game")
        else:
            raise ConnectionError('Player not found')
        
    @Pyro5.server.expose
    def player_turn(self, player, column):
        # verify game status
        if self._game_over:
            raise Exception('Game over')
        if len(self._players) < 2:
            raise Exception('Game not started')
        
        # verify play legality
        if column < 1 or column > self._dimension:
            raise ValueError('Ilegal move')
        
        
        # verify player turn
        if player != self._turn:
            raise Exception('Not your turn')
        else:
            try:
                # make move
                self.make_move(player, column)
                print(f"Player {player} moved to column {column}")
                self._move_count += 1
                
                # check win condition
                if self.check_win(player):
                    self._game_over = True
                    self._winner = player
                    print(f"Player {player} won")
                else:
                    # check draw condition
                    if self._move_count == self._dimension**2:
                        self._game_over = True
                        print('Game over')
                    else: # change turn
                        if self._turn == self._players[0]:
                            self._turn = self._players[1]
                        else:
                            self._turn = self._players[0]
                        print(f"Player {self._turn} turn")
            except Exception as e:
                raise e
        
        
    
    def make_move(self, player, column):
        move = self.get_position(column-1) # get tuple with line and column
        if (move is None):
            raise Exception('Ilegal move')
        else:
            # update last move
            self._last_move = move
            
            # update board
            if self.players[0] == player:
                self._board[move] = 1
            else:
                self._board[move] = 2
                
            
                
    def get_position(self, column):
        for i in range(0, self._dimension):
            if self._board[i][column] == 0:
                return (i, column)
            
        # if column is full
        return None
                
    def check_win(self, player):
        piece = 1 if player == self.players[0] else 2
        line_pos, col_pos = self._last_move
                
        if self.horizontal_check(piece, line_pos, col_pos):
            return True
        
        if self.vertical_check(piece, line_pos, col_pos):
            return True
        
        if self.diagonal_check(piece, line_pos, col_pos):
            return True
        
        return False


    def horizontal_check(self, piece, line_pos, col_pos):
        for i in range(col_pos - 3, col_pos + 1):
            if i < 0 or i > self._dimension - 4:
                continue
            if np.all(self._board[line_pos, i:i+4] == piece):
                return True
        return False
    
    def vertical_check(self, piece, line_pos, col_pos):
        for i in range(line_pos - 3, line_pos + 1):
            if i < 0 or i > self._dimension - 4:
                continue
            if np.all(self._board[i:i+4, col_pos] == piece):
                return True
        return False
    
    def diagonal_check(self, piece, line_pos, col_pos):
        # main diagonal
        for i in range(-3, 4):
            line_main = line_pos + i
            col_main = col_pos + i
            line_sec = line_pos + i
            col_sec = col_pos - i
            
            # check main diagonal
            if line_main < 0 or line_main + 4  > self._dimension or col_main < 0 or col_main + 4 > self._dimension:
                continue
            if np.all(np.diag(self._board[line_main:line_main+4, col_main:col_main+4]) == piece):
                return True
        
            # secondary diagonal
            if line_sec < 0 or line_sec + 4 > self._dimension  or col_sec + 1 > self._dimension or col_sec - 3 < 0:
                continue
            if np.all(np.diag(np.fliplr(self._board[line_sec:line_sec+4, col_sec-3:col_sec+1])) == piece):
                return True
        
        
        
            
                

def main():
    # cria deamon e começa loop de requesições
    Pyro5.server.serve(
        # objetos pyto que serao hosteador pelo daemon
        { FourLinesServer: "fourlines.server"},
        #use_ns=False,
        verbose=True
    )
    
    
if __name__ == '__main__':
    main()