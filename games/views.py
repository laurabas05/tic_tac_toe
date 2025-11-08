from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Game

@login_required
def game_list(request):
    games = Game.objects.all()
    return render(request, 'games/list.html', {'games': games})

@login_required
def create_game(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name', '').strip()
        if not room_name:
            return redirect('games:create')
        
        if Game.objects.filter(room_name=room_name).exists():
            return redirect('games:create')
        
        game = Game.objects.create(
            room_name=room_name,
            owner=request.user,
            board='_' * 9,
            active_player=1,
            state='active'
        )
        return redirect('games:list')
    
    return render(request, 'games/create.html')

@login_required
def game_detail(request):
    if request.method == 'POST':
        game = Game.objects.get(id=request.POST.get('name'))
        user_is_owner = (request.user == game.owner)
        
        if not request.POST.get('square'):
            board = [c for c in game.board]
            context = {
                'game': game,
                'board': board,
                'user_is_owner': user_is_owner
            }
            return render(request, 'games/detail.html', context)
        
        if game.state != 'active':
            return redirect('games:list')
        
        try:
            square = int(request.POST.get('square'))
        except (TypeError, ValueError):
            return redirect('games:list')
        
        board = list(game.board)
        if board[square] != '_':
            return redirect('games:list')
        
        token = '❌' if game.active_player == 1 else '⭕'
        board[square] = token
        game.board = ''.join(board)
        
        result = check_winner(game.board)
        if result in ('❌', '⭕'):
            game.state = 'won'
            game.winner = game.owner if result == '❌' else None
        elif result == 'Tie':
            game.state = 'tie'
        else:
            game.active_player = 2 if game.active_player == 1 else 1
            
        game.save()
        return render(request, 'games/detail.html', {'game': game, 'board': list(game.board), 'user_is_owner': user_is_owner})

    return redirect('games:list')


def check_winner(board):
    combos = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in combos:
        if board[a] != '_' and board[a] == board[b] == board[c]:
            return board[a]
    if '_' not in board:
        return 'Tie'
    return None

@login_required
def close_game(request):
    if request.method == 'POST':
        game = Game.objects.get(id=request.POST.get('name'))
        if request.user != game.owner:
            return HttpResponseForbidden("No puedes eliminar partidas de otros usuarios.")
        
        game.delete()
        return redirect('games:list')
    
    return redirect('games:list')