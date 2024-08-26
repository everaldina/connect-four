import Pyro5.api
import numpy as np
import sys
import time

class Player(object):
    def __init__(self, server):
        self._name = input('Digite seu nome: ')
        self._server = server
        
    def enter_game(self):
        self._server.join_game(self._name)
    
    def leave_game(self):
        self._server.leave_game(self._name)
        
    def print_board(self):
        board = self._server.board
        lines = columns = self._server.dimension
        
        # print column numbers
        for i in range(columns):
            print(f'  {i+1} ', end='')
        print()
        print(f"{' ---'*columns}")
        
        # print board
        for i in range(lines):
            for j in range(columns):
                piece = board[i][j]
                if piece == 0:
                    piece = ' '
                print(f"| {piece} ", end='')
            print('|')
            print(f"{' ---'*columns}")
        
        
    def play_turn(self):
        try: 
            column = int(input('Digite a coluna: '))
            self._server.player_turn(self._name, column)
        except ValueError:
            print('Digite um número válido')
            self.play_turn()
        except Exception as e:
            print(e)
            self.play_turn()

        
def main():
    # set excepthook to Pyro's excepthook
    sys.excepthook = Pyro5.errors.excepthook
    
    # locate nameserver and get server uri
    nameserver = Pyro5.api.locate_ns()
    uri = nameserver.lookup('fourlines.server')
    
    # connect to server
    with Pyro5.api.Proxy(uri) as server:
        # create player
        player = Player(server)
        
        # enter game
        try:
            player.enter_game()
        except Exception as e:
            print(e)
            return
        
        # play game
        play = True
        while play:
            # wait for another player
            if len(server.players) < 2:
                print('Aguardando outro jogador...')
                time.sleep(5)
            else:
                # print informations
                print('Jogo iniciado')
                print(f'Jogador 1: {server.players[0]}')
                print(f'Jogador 2: {server.players[1]}')
                
                # playing loop
                while not server.game_over:
                    if server.turn == player._name and not server.game_over:
                        print('Sua vez')
                        player.print_board()
                        player.play_turn()
                        if not server.game_over:
                            print('Aguardando jogada do outro jogador')
                        else:
                            break
                        
                # end game messages
                if server.winner is not None and server.winner == player._name:
                    print('Parabens, você ganhou!!!')
                elif server.winner is not None:
                    player.print_board()
                    print(f'Jogador {server.winner} ganhou')
                else:
                    print('Empate')
                    
                # leave game
                play = False
                time.sleep(3)
                player.leave_game()
                

if __name__ == '__main__':
    main()