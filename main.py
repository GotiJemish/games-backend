import random
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
from typing import Dict, List

from db_connect import init_db, get_session, engine
from models import Game, Player
from pydantic import BaseModel

# Create a connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, game_id: str, websocket: WebSocket):
        if game_id in self.active_connections:
            if websocket in self.active_connections[game_id]:
                self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast(self, game_id: str, message: dict):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()

def serialize_game(game: Game) -> dict:
    return {
        "id": game.id,
        "game_type": game.game_type,
        "status": game.status,
        "current_turn": game.current_turn,
        "last_roll": game.last_roll,
        "has_rolled": game.has_rolled,
        "winner": game.winner,
        "board_state": game.board_state,
        "players": [
            {"username": p.username, "color": p.color} for p in game.players
        ]
    }

async def handle_bot_turns(game_id: str):
    import asyncio
    from sqlmodel import Session
    from db_connect import engine
    from models import Game, Player
    
    with Session(engine) as db:
        db_game = db.get(Game, game_id)
        if not db_game or db_game.status != "playing":
            return
            
        current_player = next((p for p in db_game.players if p.color == db_game.current_turn), None)
        if not current_player:
            return
            
        if current_player.username.startswith("Computer (Bot)"):
            # Wait 1 second to make it feel natural
            await asyncio.sleep(1.0)
            
            # Fetch fresh state in case anything changed
            db.refresh(db_game)
            if db_game.status != "playing" or db_game.current_turn != current_player.color:
                return
                
            if db_game.game_type == "go":
                from gameLogic.go.bot import get_bot_move
                from gameLogic.go.logic import make_move as go_make_move, calculate_score
                from gameLogic.go.rules import get_next_turn_go
                
                row, col, pass_turn = get_bot_move(db_game.board_state, current_player.color)
                
                if pass_turn:
                    db_game.board_state["consecutive_passes"] += 1
                    msg = f"{current_player.username} passed."
                    
                    if db_game.board_state["consecutive_passes"] >= 2:
                        score = calculate_score(db_game.board_state)
                        db_game.status = "finished"
                        db_game.winner = score["winner"]
                        db_game.current_turn = None
                        msg += f" Both players passed. Game ended! Scores - Black: {score['BLACK']}, White: {score['WHITE']}. Winner: {score['winner']}!"
                    else:
                        db_game.current_turn = get_next_turn_go(current_player.color)
                        
                    db_game.has_rolled = False
                    db_game.last_roll = None
                    
                    db.add(db_game)
                    db.commit()
                    db.refresh(db_game)
                    
                    await manager.broadcast(game_id, {
                        "type": "move",
                        "username": current_player.username,
                        "color": current_player.color,
                        "message": msg,
                        "game": serialize_game(db_game)
                    })
                else:
                    new_board_state, success, move_desc = go_make_move(db_game.board_state, current_player.color, row, col)
                    if success:
                        db_game.board_state = new_board_state
                        db_game.current_turn = get_next_turn_go(current_player.color)
                        db_game.has_rolled = False
                        db_game.last_roll = None
                        
                        db.add(db_game)
                        db.commit()
                        db.refresh(db_game)
                        
                        await manager.broadcast(game_id, {
                            "type": "move",
                            "username": current_player.username,
                            "color": current_player.color,
                            "message": move_desc,
                            "game": serialize_game(db_game)
                        })
                        
            elif db_game.game_type == "snake-ladder":
                from gameLogic.snake_ladder.logic import make_move as sl_make_move, check_winner as sl_check_winner
                from gameLogic.snake_ladder.rules import get_next_turn
                
                roll = random.randint(1, 6)
                new_board_state, move_desc = sl_make_move(db_game.board_state, current_player.color, roll)
                db_game.board_state = new_board_state
                db_game.last_roll = roll
                db_game.has_rolled = False
                
                winner = sl_check_winner(new_board_state)
                if winner:
                    db_game.status = "finished"
                    db_game.winner = winner
                    db_game.current_turn = None
                    move_desc += f" {current_player.username} HAS WON THE GAME!"
                else:
                    if roll == 6:
                        move_desc += f" {current_player.username} gets another turn!"
                    else:
                        active_colors = [p.color for p in db_game.players]
                        next_color = get_next_turn(current_player.color, active_colors)
                        db_game.current_turn = next_color
                        
                db.add(db_game)
                db.commit()
                db.refresh(db_game)
                
                await manager.broadcast(game_id, {
                    "type": "move",
                    "username": current_player.username,
                    "color": current_player.color,
                    "roll": roll,
                    "message": move_desc,
                    "game": serialize_game(db_game)
                })
                
            elif db_game.game_type == "ludo":
                from gameLogic.ludo.bot import get_bot_move
                from gameLogic.ludo.logic import make_move as ludo_make_move, check_winner as ludo_check_winner
                from gameLogic.ludo.rules import get_next_turn
                
                roll = random.randint(1, 6)
                db_game.last_roll = roll
                
                token_idx = get_bot_move(db_game.board_state, current_player.color, roll)
                
                if token_idx == -1:
                    active_colors = [p.color for p in db_game.players]
                    next_color = get_next_turn(current_player.color, active_colors)
                    db_game.current_turn = next_color
                    db_game.has_rolled = False
                    db_game.last_roll = None
                    msg = f"{current_player.username} rolled a {roll} and has no valid moves. Turn passes to {next_color}."
                    
                    db.add(db_game)
                    db.commit()
                    db.refresh(db_game)
                    
                    await manager.broadcast(game_id, {
                        "type": "roll",
                        "username": current_player.username,
                        "color": current_player.color,
                        "roll": roll,
                        "message": msg,
                        "game": serialize_game(db_game)
                    })
                else:
                    board_copy = {k: list(v) for k, v in db_game.board_state.items()}
                    new_board_state, captured, move_desc = ludo_make_move(board_copy, current_player.color, token_idx, roll)
                    
                    db_game.board_state = new_board_state
                    db_game.last_roll = roll
                    db_game.has_rolled = False
                    
                    winner = ludo_check_winner(new_board_state)
                    if winner:
                        db_game.status = "finished"
                        db_game.winner = winner
                        db_game.current_turn = None
                        move_desc += f" {winner} HAS WON THE GAME!"
                    else:
                        if roll == 6 or captured:
                            move_desc += f" {current_player.color} gets another roll!"
                        else:
                            active_colors = [p.color for p in db_game.players]
                            next_color = get_next_turn(current_player.color, active_colors)
                            db_game.current_turn = next_color
                    
                    db.add(db_game)
                    db.commit()
                    db.refresh(db_game)
                    
                    await manager.broadcast(game_id, {
                        "type": "move",
                        "username": current_player.username,
                        "color": current_player.color,
                        "roll": roll,
                        "message": move_desc,
                        "game": serialize_game(db_game)
                    })
            
            # Chain play recursively if next player is also a bot
            asyncio.create_task(handle_bot_turns(game_id))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

class CreateGameRequest(BaseModel):
    username: str
    color: str
    game_type: str = "ludo"  # "ludo", "snake-ladder", "go"
    board_size: int = 9      # For Go: 9, 13, 19

class JoinGameRequest(BaseModel):
    username: str
    color: str

@app.get('/')
def read_root():
    return {"message": "Ludo Backend is running!"}

@app.post("/games/create")
def create_game(req: CreateGameRequest, session: Session = Depends(get_session)):
    color_upper = req.color.upper()
    game_type_lower = req.game_type.lower()
    
    if game_type_lower not in ["ludo", "snake-ladder", "go"]:
        raise HTTPException(status_code=400, detail="Game type must be ludo, snake-ladder, or go")
        
    if game_type_lower == "go":
        if color_upper not in ["BLACK", "WHITE"]:
            raise HTTPException(status_code=400, detail="Color for Go must be BLACK or WHITE")
    else:
        if color_upper not in ["RED", "GREEN", "YELLOW", "BLUE"]:
            raise HTTPException(status_code=400, detail="Color must be RED, GREEN, YELLOW, or BLUE")
        
    # Store initial board_size inside board_state
    initial_board_state = {"size": req.board_size} if game_type_lower == "go" else {}
    game = Game(game_type=game_type_lower, board_state=initial_board_state)
    session.add(game)
    session.commit()
    session.refresh(game)
    
    player = Player(game_id=game.id, username=req.username, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    return serialize_game(game)

@app.post("/games/{game_id}/join")
def join_game(game_id: str, req: JoinGameRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Cannot join a game that has already started or finished")
        
    max_players = 2 if game.game_type == "go" else 4
    if len(game.players) >= max_players:
        raise HTTPException(status_code=400, detail=f"Game is full (max {max_players} players)")
        
    color_upper = req.color.upper()
    if game.game_type == "go":
        if color_upper not in ["BLACK", "WHITE"]:
            raise HTTPException(status_code=400, detail="Color for Go must be BLACK or WHITE")
    else:
        if color_upper not in ["RED", "GREEN", "YELLOW", "BLUE"]:
            raise HTTPException(status_code=400, detail="Color must be RED, GREEN, YELLOW, or BLUE")
        
    for p in game.players:
        if p.color == color_upper:
            raise HTTPException(status_code=400, detail=f"Color {color_upper} is already taken")
        if p.username == req.username:
            raise HTTPException(status_code=400, detail=f"Username {req.username} is already taken in this game")
            
    player = Player(game_id=game_id, username=req.username, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    return serialize_game(game)

@app.post("/games/{game_id}/add_bot")
async def add_bot(game_id: str, req: JoinGameRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Cannot add bot to a game that has already started or finished")
        
    max_players = 2 if game.game_type == "go" else 4
    if len(game.players) >= max_players:
        raise HTTPException(status_code=400, detail=f"Game is full (max {max_players} players)")
        
    color_upper = req.color.upper()
    if game.game_type == "go":
        if color_upper not in ["BLACK", "WHITE"]:
            raise HTTPException(status_code=400, detail="Color for Go must be BLACK or WHITE")
    else:
        if color_upper not in ["RED", "GREEN", "YELLOW", "BLUE"]:
            raise HTTPException(status_code=400, detail="Color must be RED, GREEN, YELLOW, or BLUE")
        
    for p in game.players:
        if p.color == color_upper:
            raise HTTPException(status_code=400, detail=f"Color {color_upper} is already taken")
            
    bot_name = f"Computer (Bot) {color_upper}"
    player = Player(game_id=game_id, username=bot_name, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    import asyncio
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "system",
        "message": f"{bot_name} ({color_upper}) has joined the lobby."
    }))
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "state",
        "game": serialize_game(game)
    }))
    
    return serialize_game(game)

@app.post("/games/{game_id}/start")
async def start_game(game_id: str, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Game has already started or finished")
    if len(game.players) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
        
    active_colors = [p.color for p in game.players]
    if game.game_type == "snake-ladder":
        from gameLogic.snake_ladder.logic import initialize_board
        game.board_state = initialize_board(active_colors)
        if "RED" in active_colors:
            game.current_turn = "RED"
        else:
            game.current_turn = active_colors[0]
    elif game.game_type == "go":
        from gameLogic.go.logic import initialize_board
        size = game.board_state.get("size", 9)
        game.board_state = initialize_board(size)
        game.current_turn = "BLACK"  # Black always plays first
    else:
        from gameLogic.ludo.logic import initialize_board
        game.board_state = initialize_board(active_colors)
        if "RED" in active_colors:
            game.current_turn = "RED"
        else:
            game.current_turn = active_colors[0]
        
    game.status = "playing"
    game.has_rolled = False
    game.last_roll = None
    
    session.add(game)
    session.commit()
    session.refresh(game)
    
    import asyncio
    asyncio.create_task(handle_bot_turns(game.id))
    
    return serialize_game(game)

@app.websocket("/games/{game_id}/ws")
async def websocket_endpoint(websocket: WebSocket, game_id: str, username: str):
    # Establish separate db transaction for verification
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game:
            await websocket.accept()
            await websocket.close(code=4004, reason="Game not found")
            return
            
        player = session.exec(
            select(Player).where(Player.game_id == game_id, Player.username == username)
        ).first()
        if not player:
            await websocket.accept()
            await websocket.close(code=4003, reason="Player not registered in this game")
            return
            
        player_color = player.color

    await manager.connect(game_id, websocket)
    
    # Broadcast join event
    await manager.broadcast(game_id, {
        "type": "system",
        "message": f"{username} ({player_color}) has connected to the game."
    })
    
    # Send current state
    with Session(engine) as session:
        db_game = session.get(Game, game_id)
        await websocket.send_json({
            "type": "state",
            "game": serialize_game(db_game)
        })
    
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            
            with Session(engine) as db:
                db_game = db.get(Game, game_id)
                db_player = db.exec(
                    select(Player).where(Player.game_id == game_id, Player.username == username)
                ).first()
                
                if not db_game or not db_player:
                    await websocket.send_json({"type": "error", "message": "Game or player context lost."})
                    continue
                    
                if db_game.status == "waiting" and action in ["roll_dice", "move_token"]:
                    await websocket.send_json({"type": "error", "message": "Game has not started yet."})
                    continue
                if db_game.status == "finished" and action in ["roll_dice", "move_token"]:
                    await websocket.send_json({"type": "error", "message": "Game is already finished."})
                    continue
                    
                if action == "roll_dice":
                    if db_game.current_turn != db_player.color:
                        await websocket.send_json({"type": "error", "message": "It is not your turn."})
                        continue
                    if db_game.game_type == "snake-ladder":
                        # Snakes & Ladders automatic move logic
                        roll = random.randint(1, 6)
                        from gameLogic.snake_ladder import make_move as sl_make_move, check_winner as sl_check_winner
                        from gameLogic.ludo import get_next_turn
                        
                        new_board_state, move_desc = sl_make_move(db_game.board_state, db_player.color, roll)
                        db_game.board_state = new_board_state
                        db_game.last_roll = roll
                        db_game.has_rolled = False
                        
                        winner = sl_check_winner(new_board_state)
                        if winner:
                            db_game.status = "finished"
                            db_game.winner = winner
                            db_game.current_turn = None
                            move_desc += f" {db_player.username} HAS WON THE GAME!"
                        else:
                            if roll == 6:
                                move_desc += f" {db_player.username} rolled a 6 and gets another turn!"
                            else:
                                active_colors = [p.color for p in db_game.players]
                                next_color = get_next_turn(db_player.color, active_colors)
                                db_game.current_turn = next_color
                        
                        db.add(db_game)
                        db.commit()
                        db.refresh(db_game)
                        
                        await manager.broadcast(game_id, {
                            "type": "move",  # broadcast as a move event
                            "username": db_player.username,
                            "color": db_player.color,
                            "roll": roll,
                            "message": move_desc,
                            "game": serialize_game(db_game)
                        })
                        import asyncio
                        asyncio.create_task(handle_bot_turns(game_id))
                    else:
                        # Ludo standard roll logic
                        if db_game.has_rolled:
                            await websocket.send_json({"type": "error", "message": "You have already rolled. Move a token."})
                            continue
                            
                        roll = random.randint(1, 6)
                        db_game.last_roll = roll
                        db_game.has_rolled = True
                        
                        tokens = db_game.board_state[db_player.color]
                        msg = f"{db_player.username} ({db_player.color}) rolled a {roll}."
                        
                        from gameLogic.ludo.rules import has_valid_moves, get_next_turn
                        if not has_valid_moves(db_player.color, tokens, roll):
                            db_game.has_rolled = False
                            active_colors = [p.color for p in db_game.players]
                            next_color = get_next_turn(db_player.color, active_colors)
                            db_game.current_turn = next_color
                            msg += f" No valid moves available. Turn passes to {next_color}."
                        
                        db.add(db_game)
                        db.commit()
                        db.refresh(db_game)
                        
                        await manager.broadcast(game_id, {
                            "type": "roll",
                            "username": db_player.username,
                            "color": db_player.color,
                            "roll": roll,
                            "message": msg,
                            "game": serialize_game(db_game)
                        })
                        import asyncio
                        asyncio.create_task(handle_bot_turns(game_id))
                    
                elif action == "move_token":
                    if db_game.current_turn != db_player.color:
                        await websocket.send_json({"type": "error", "message": "It is not your turn."})
                        continue
                    if not db_game.has_rolled:
                        await websocket.send_json({"type": "error", "message": "You need to roll the dice first."})
                        continue
                        
                    token_idx = data.get("token_idx")
                    if token_idx is None or not (0 <= token_idx <= 3):
                        await websocket.send_json({"type": "error", "message": "Invalid token index (must be 0 to 3)."})
                        continue
                        
                    from gameLogic.ludo.logic import make_move, check_winner
                    from gameLogic.ludo.rules import get_next_turn
                    
                    board_copy = {k: list(v) for k, v in db_game.board_state.items()}
                    new_board_state, captured, move_desc = make_move(
                        board_copy, db_player.color, token_idx, db_game.last_roll
                    )
                    
                    if new_board_state[db_player.color][token_idx] == db_game.board_state[db_player.color][token_idx]:
                        await websocket.send_json({"type": "error", "message": f"Invalid move: {move_desc}"})
                        continue
                        
                    db_game.board_state = new_board_state
                    
                    winner = check_winner(new_board_state)
                    if winner:
                        db_game.status = "finished"
                        db_game.winner = winner
                        db_game.current_turn = None
                        move_desc += f" {winner} HAS WON THE GAME!"
                    else:
                        if db_game.last_roll == 6 or captured:
                            move_desc += f" {db_player.color} gets another roll!"
                        else:
                            active_colors = [p.color for p in db_game.players]
                            next_color = get_next_turn(db_player.color, active_colors)
                            db_game.current_turn = next_color
                            
                    db_game.has_rolled = False
                    
                    db.add(db_game)
                    db.commit()
                    db.refresh(db_game)
                    
                    await manager.broadcast(game_id, {
                        "type": "move",
                        "username": db_player.username,
                        "color": db_player.color,
                        "token_idx": token_idx,
                        "message": move_desc,
                        "game": serialize_game(db_game)
                    })
                    import asyncio
                    asyncio.create_task(handle_bot_turns(game_id))
                    
                elif action == "place_stone":
                    if db_game.game_type != "go":
                        await websocket.send_json({"type": "error", "message": "Action not allowed for this game type."})
                        continue
                    if db_game.current_turn != db_player.color:
                        await websocket.send_json({"type": "error", "message": "It is not your turn."})
                        continue
                        
                    pass_turn = data.get("pass_turn", False)
                    
                    if pass_turn:
                        db_game.board_state["consecutive_passes"] += 1
                        from gameLogic.go.rules import get_next_turn_go as go_get_next_turn
                        from gameLogic.go.logic import calculate_score
                        
                        msg = f"{db_player.username} ({db_player.color}) passed."
                        
                        if db_game.board_state["consecutive_passes"] >= 2:
                            score = calculate_score(db_game.board_state)
                            db_game.status = "finished"
                            db_game.winner = score["winner"]
                            db_game.current_turn = None
                            msg += f" Both players passed. Game ended! Scores - Black: {score['BLACK']}, White: {score['WHITE']}. Winner: {score['winner']}!"
                        else:
                            db_game.current_turn = go_get_next_turn(db_player.color)
                            
                        db_game.has_rolled = False
                        db_game.last_roll = None
                        
                        db.add(db_game)
                        db.commit()
                        db.refresh(db_game)
                        
                        await manager.broadcast(game_id, {
                            "type": "move",
                            "username": db_player.username,
                            "color": db_player.color,
                            "message": msg,
                            "game": serialize_game(db_game)
                        })
                        import asyncio
                        asyncio.create_task(handle_bot_turns(game_id))
                        
                    else:
                        row = data.get("row")
                        col = data.get("col")
                        if row is None or col is None:
                            await websocket.send_json({"type": "error", "message": "Row and Col are required."})
                            continue
                            
                        from gameLogic.go.logic import make_move as go_make_move
                        from gameLogic.go.rules import get_next_turn_go as go_get_next_turn
                        
                        new_board_state, success, move_desc = go_make_move(db_game.board_state, db_player.color, row, col)
                        if not success:
                            await websocket.send_json({"type": "error", "message": move_desc})
                            continue
                            
                        db_game.board_state = new_board_state
                        db_game.current_turn = go_get_next_turn(db_player.color)
                        db_game.has_rolled = False
                        db_game.last_roll = None
                        
                        db.add(db_game)
                        db.commit()
                        db.refresh(db_game)
                        
                        await manager.broadcast(game_id, {
                            "type": "move",
                            "username": db_player.username,
                            "color": db_player.color,
                            "message": move_desc,
                            "game": serialize_game(db_game)
                        })
                        import asyncio
                        asyncio.create_task(handle_bot_turns(game_id))
                        
                elif action == "chat":
                    msg = data.get("message", "")
                    if msg:
                        await manager.broadcast(game_id, {
                            "type": "chat",
                            "username": db_player.username,
                            "color": db_player.color,
                            "message": msg
                        })
                        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(game_id, websocket)
        await manager.broadcast(game_id, {
            "type": "system",
            "message": f"{username} has disconnected."
        })