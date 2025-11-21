from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Game
import re

# Lista de juegos
@login_required
def game_list(request):
    games = Game.objects.all()
    return render(request, 'games/list.html', {'games': games})

# Crear la partida
@login_required
def create_game(request):
    if request.method == 'POST':
        # comrpobar q el nombre de la sala es válido (por tema ws)
        room_name = request.POST.get('room_name', '').strip()
        room_name = room_name.lower()
        room_name = room_name.replace(" ", "-")
        room_name = re.sub(r"[^a-z0-9-_\.]", "", room_name)
        
        # no has introducido nombre
        if not room_name:
            return redirect('games:create')
        
        # ya existe una partida con ese nombre
        if Game.objects.filter(room_name=room_name).exists():
            return redirect('games:create')
        
        # crea la partida
        game = Game.objects.create(
            room_name=room_name,
            owner=request.user,
            board='_' * 9,
            active_player=1,
            state='active'
        )
        return redirect('games:list')
    
    return render(request, 'games/create.html')

# Partida en detalle
@login_required
def game_detail(request, game_id):

    game = Game.objects.get(id=game_id)
    
    # el q ha entrado es el q la ha creado?
    user_is_owner = (request.user == game.owner)

    # convierte el tablero en una lista para mostrarlo más
    # fácilmente en la plantilla.
    board = list(game.board)

    return render(request, 'games/detail.html', {
        'game': game,
        'board': board,
        'user_is_owner': user_is_owner
    })

# Decidir ganador
def check_winner(board):
    # combinaciones ganadoras
    combos = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    
    # para cada trío de posiciones que forme una línea ganadora
    for a, b, c in combos:
        # la casilla no está vacía y las tres casillas tienen el mismo valor
        if board[a] != '_' and board[a] == board[b] == board[c]:
            # devuelve el símbolo ganador ('X' o 'O')
            return board[a]
        
    # no quedan huecos: empate
    if '_' not in board:
        return 'Tie'
    
    # no hay ganador: nada
    return None

# Eliminar la partida
@login_required
def close_game(request):
    if request.method == 'POST':
        game = Game.objects.get(id=request.POST.get('name'))
        
        # elimina la partida con su id (que se envía desde el form)
        game.delete()
        return redirect('games:list')
    
    return redirect('games:list')