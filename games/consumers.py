# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Game

# combinaciones ganadoras
WIN_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),
    (0,3,6),(1,4,7),(2,5,8),
    (0,4,8),(2,4,6)
]


# devuelve un diccionario con la info actual de la partida
@database_sync_to_async
def db_get_game_payload_by_room(room_name):
    game = Game.objects.get(room_name=room_name)
    
    # determinar token y username del jugador q tiene el turno
    if game.active_player == 1:
        turn = "❌"
        turn_username = game.owner.username if game.owner else None
    elif game.active_player == 2:
        turn = "⭕"
        turn_username = game.player2.username if game.player2 else None
    else:
        turn = None
        turn_username = None
    
    return {
        "id": game.id,
        "room_name": game.room_name,
        "board": game.board,
        "active_player": game.active_player,
        "state": game.state,
        "winner_username": game.winner.username if game.winner else None,
        "owner_id": game.owner.id,
        "player2_id": game.player2.id if game.player2 else None,
        "turn": turn,
        "turn_username": turn_username,
    }


# si player2 entra a la partida, se asigna, y se devuelve
# el payload actual
@database_sync_to_async
def db_assign_player2_and_get_payload(game_id, user_id):
    game = Game.objects.get(id=game_id)

    # si el owner entra, no hacemos nada. si player2 está libre
    # lo asignamos. Pero si user no existe, nada.
    if game.owner.id != user_id and game.player2 is None:
        try:
            user = User.objects.get(id=user_id)
            game.player2 = user
            game.save()
        except User.DoesNotExist:
            # no hacemos nada si user no existe
            pass
        
    # determinar token y username del jugador que tiene el turno
    if game.active_player == 1:
        turn = "❌"
        turn_username = game.owner.username if game.owner else None
    elif game.active_player == 2:
        turn = "⭕"
        turn_username = game.player2.username if game.player2 else None
    else:
        turn = None
        turn_username = None

    # reconstruimos payload y lo devolvemos tras posible
    # asignación de player2
    return {
        "id": game.id,
        "room_name": game.room_name,
        "board": game.board,
        "active_player": game.active_player,
        "state": game.state,
        "winner_username": game.winner.username if game.winner else None,
        "owner_id": game.owner.id,
        "player2_id": game.player2.id if game.player2 else None,
        "turn": turn,
        "turn_username": turn_username,
    }


# gestiona la jugada completa
@database_sync_to_async
def db_process_move_and_get_payload(game_id, user_id, index):
    game = Game.objects.get(id=game_id)

    # si el juego no está activo, no deja mover
    if game.state != "active":
        return None

    # si le toca jugador 2 pero aún no existe, no permite mover
    if game.active_player == 2 and not game.player2:
        return None

    # comprueba qué usuario es el q tiene q mover
    expected_user = game.owner.id if game.active_player == 1 else (game.player2.id if game.player2 else None)
    # si el user_id q intenta mover no coincide con
    # expected_user, no le permite mover
    if expected_user != user_id:
        return None

    # convierte el tablero a una lista para poder
    # modificarlo por indice
    board = list(game.board)

    # comprueba q la casilla está vacía y está entre 1 y 9
    if index < 0 or index > 8 or board[index] != "_":
        return None

    # decide el token a colocar depende de q sea j1 o j2
    token = "❌" if game.active_player == 1 else "⭕"
    # lo inserta en la posición index
    board[index] = token
    game.board = "".join(board)

    # comprobar ganador dependiendo de las combinaciones ganadoras
    winner_token = None
    for a,b,c in WIN_COMBOS:
        if board[a] != "_" and board[a] == board[b] == board[c]:
            # asigna el token ganador
            winner_token = board[a]
            break

    # si hay token ganador, se asigna estado y jugador ganador
    if winner_token:
        game.state = "won"
        game.winner = game.owner if winner_token == "❌" else game.player2
    # si no hay ganador ni casillas libres, empate
    elif "_" not in board:
        game.state = "tie"
        game.winner = None
    # si no hay ganador ni empate, se cambia el turno
    else:
        game.active_player = 2 if game.active_player == 1 else 1

    # guarda los cambios en la base de datos
    game.save()

    # determinar token y username del jugador que tiene el turno tras la jugada
    if game.active_player == 1:
        turn = "❌"
        turn_username = game.owner.username if game.owner else None
    elif game.active_player == 2:
        turn = "⭕"
        turn_username = game.player2.username if game.player2 else None
    else:
        turn = None
        turn_username = None

    # devuelve el payload actualizado
    return {
        "id": game.id,
        "room_name": game.room_name,
        "board": game.board,
        "active_player": game.active_player,
        "state": game.state,
        "winner_username": game.winner.username if game.winner else None,
        "owner_id": game.owner.id,
        "player2_id": game.player2.id if game.player2 else None,
        "turn": turn,
        "turn_username": turn_username,
    }


# 
class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # obtener room_name desde ruta
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # construye un nombre de grupo único para Channels.
        # los jugadores de la misma sala estarán en este grupo.
        self.room_group_name = f"game_{self.room_name}"

        # añade este channel al grupo
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # aceptar siempre la conexión
        await self.accept()

    async def disconnect(self, close_code):
        # al desconectarse, elimina este chanel del grupo
        # para que no reciba más eventos
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # llega un msg desde el cliente y lo parsea como JSON
        try:
            data = json.loads(text_data)
        except Exception:
            return

        # extrae la acción q pide el cliente (join o move)
        action = data.get("action")

        # llama a la función para obtener el estado actual del juego
        try:
            game_payload = await db_get_game_payload_by_room(self.room_name)
        # la partida no existe
        except Game.DoesNotExist:
            return

        if action == "join":
            # intentar extraer user_id del json y convertirlo a int
            try:
                user_id = int(data.get("user_id"))
            except (TypeError, ValueError):
                return

            # llama a la funcion q intenta asignar player2
            updated_payload = await db_assign_player2_and_get_payload(game_payload["id"], user_id)

            # envia al grupo un evento q sera manejado por el metodo game_update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_update",
                    "payload": updated_payload
                }
            )

        # accion move, se extrae user_id e indice
        elif action == "move":
            try:
                user_id = int(data.get("user_id"))
                index = int(data.get("index"))
            except (TypeError, ValueError):
                return

            # llama a la funcion q procesa la jugada
            result_payload = await db_process_move_and_get_payload(game_payload["id"], user_id, index)
            # si no es valida no se propaga nada
            if not result_payload:
                return

            # si la jugada es valida manda el payload a todo el grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_update",
                    "payload": result_payload
                }
            )

    # se llama cuando group_send envia un evento
    async def game_update(self, event):
        # extrae el payload y lo envía al cliente
        payload = event.get("payload", {})
        await self.send(text_data=json.dumps(payload))
