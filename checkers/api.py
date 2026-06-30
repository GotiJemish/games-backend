from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
import asyncio
from db_connect import get_session, engine
from models import Game, Player
from shared import manager, serialize_game
from pydantic import BaseModel

router = APIRouter()

class CreateLobbyRequest(BaseModel):
    username: str
    color: str
    difficulty: str = "medium"

class JoinLobbyRequest(BaseModel):
    username: str
    color: str


async def handle_bot_turns(game_id: str):
    with Session(engine) as db:
        db_game = db.get(Game, game_id)
        if not db_game or db_game.status != "playing" or db_game.game_type != "checkers":
            return
            
        current_player = next((p for p in db_game.players if p.color == db_game.current_turn), None)
        if not current_player or not current_player.username.startswith("Computer (Bot)"):
            return
            
        await asyncio.sleep(1.0)
        db.refresh(db_game)
        if db_game.status != "playing" or db_game.current_turn != current_player.color:
            return
            
        from checkers.bot import get_bot_move
        from checkers.logic import make_move as checkers_make_move
        from checkers.rules import get_next_turn_checkers, check_winner_checkers
        
        difficulty = db_game.board_state.get("difficulty", "medium")
        bot_move = get_bot_move(db_game.board_state, current_player.color, difficulty)
        
        if bot_move is None:
            return
            
        from_pos, to_pos = bot_move
        new_board_state, success, move_desc = checkers_make_move(
            db_game.board_state, current_player.color, from_pos, to_pos
        )
        
        if success:
            db_game.board_state = new_board_state
            
            # Check for chain jumps
            if new_board_state.get("chain_from") is not None:
                # Bot has a chain jump available, handle it
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
                # Continue chain jump
                asyncio.create_task(handle_bot_turns(game_id))
                return
            
            winner = check_winner_checkers(new_board_state)
            if winner:
                db_game.status = "finished"
                db_game.winner = winner
                db_game.current_turn = None
                move_desc += f" Game Over! Winner: {winner}"
            else:
                db_game.current_turn = get_next_turn_checkers(current_player.color)
                
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
            
        asyncio.create_task(handle_bot_turns(game_id))


@router.post("/createLobby")
def create_lobby(req: CreateLobbyRequest, session: Session = Depends(get_session)):
    color_upper = req.color.upper()
    if color_upper not in ["RED", "BLACK"]:
        raise HTTPException(status_code=400, detail="Color for Checkers must be RED or BLACK")
        
    from checkers.logic import initialize_board
    initial_board_state = initialize_board(req.difficulty)
    game = Game(game_type="checkers", board_state=initial_board_state)
    session.add(game)
    player = Player(game_id=game.id, username=req.username, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    return serialize_game(game)


@router.post("/{game_id}/joinLobby")
async def join_lobby(game_id: str, req: JoinLobbyRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game or game.game_type != "checkers":
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Cannot join a game that has already started or finished")
        
    if len(game.players) >= 2:
        raise HTTPException(status_code=400, detail="Game is full (max 2 players)")
        
    color_upper = req.color.upper()
    if color_upper not in ["RED", "BLACK"]:
        raise HTTPException(status_code=400, detail="Color for Checkers must be RED or BLACK")
        
    for p in game.players:
        if p.color == color_upper:
            raise HTTPException(status_code=400, detail=f"Color {color_upper} is already taken")
        if p.username == req.username:
            raise HTTPException(status_code=400, detail=f"Username {req.username} is already taken in this game")
            
    player = Player(game_id=game_id, username=req.username, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "system",
        "message": f"{req.username} ({color_upper}) has joined the lobby."
    }))
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "state",
        "game": serialize_game(game)
    }))
    
    return serialize_game(game)


@router.post("/{game_id}/add_bot")
async def add_bot(game_id: str, req: JoinLobbyRequest, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game or game.game_type != "checkers":
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Cannot add bot to a game that has already started or finished")
        
    if len(game.players) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
        
    color_upper = req.color.upper()
    if color_upper not in ["RED", "BLACK"]:
        raise HTTPException(status_code=400, detail="Color for Checkers must be RED or BLACK")
        
    for p in game.players:
        if p.color == color_upper:
            raise HTTPException(status_code=400, detail=f"Color {color_upper} is already taken")
            
    bot_name = f"Computer (Bot) {color_upper}"
    player = Player(game_id=game_id, username=bot_name, color=color_upper)
    session.add(player)
    session.commit()
    session.refresh(game)
    
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "system",
        "message": f"{bot_name} ({color_upper}) has joined the lobby."
    }))
    asyncio.create_task(manager.broadcast(game_id, {
        "type": "state",
        "game": serialize_game(game)
    }))
    
    return serialize_game(game)


@router.post("/{game_id}/start")
async def start_game(game_id: str, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game or game.game_type != "checkers":
        raise HTTPException(status_code=404, detail="Game not found")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Game has already started or finished")
    if len(game.players) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 players to start")
        
    from checkers.logic import initialize_board
    difficulty = game.board_state.get("difficulty", "medium")
    game.board_state = initialize_board(difficulty=difficulty)
    game.current_turn = "RED"  # Red always plays first in checkers
    
    game.status = "playing"
    game.has_rolled = False
    game.last_roll = None
    
    session.add(game)
    session.commit()
    session.refresh(game)
    
    asyncio.create_task(manager.broadcast(game.id, {
        "type": "state",
        "game": serialize_game(game)
    }))
    asyncio.create_task(handle_bot_turns(game.id))
    
    return serialize_game(game)


@router.websocket("/{game_id}/ws")
async def websocket_endpoint(websocket: WebSocket, game_id: str, username: str):
    with Session(engine) as session:
        game = session.get(Game, game_id)
        if not game or game.game_type != "checkers":
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
    
    await manager.broadcast(game_id, {
        "type": "system",
        "message": f"{username} ({player_color}) has connected to the game."
    })
    
    with Session(engine) as session:
        db_game = session.get(Game, game_id)
        await manager.broadcast(game_id, {
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
                    
                if action == "chat":
                    await manager.broadcast(game_id, {
                        "type": "chat",
                        "username": db_player.username,
                        "color": db_player.color,
                        "message": data.get("message")
                    })
                    continue
                    
                if action == "move_piece":
                    if db_game.status != "playing":
                        await websocket.send_json({"type": "error", "message": "Game is not playing."})
                        continue
                    if db_game.current_turn != db_player.color:
                        await websocket.send_json({"type": "error", "message": "It is not your turn."})
                        continue
                        
                    from_pos = data.get("from_pos")
                    to_pos = data.get("to_pos")
                    if from_pos is None or to_pos is None:
                        await websocket.send_json({"type": "error", "message": "from_pos and to_pos are required."})
                        continue
                        
                    from checkers.logic import make_move as checkers_make_move
                    from checkers.rules import get_next_turn_checkers, check_winner_checkers
                    
                    new_board_state, success, move_desc = checkers_make_move(
                        db_game.board_state, db_player.color, from_pos, to_pos
                    )
                    if not success:
                        await websocket.send_json({"type": "error", "message": move_desc})
                        continue
                        
                    db_game.board_state = new_board_state
                    
                    # Check for chain jumps
                    if new_board_state.get("chain_from") is not None:
                        # Player has more captures from this position, don't switch turns
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
                        continue
                    
                    winner = check_winner_checkers(new_board_state)
                    if winner:
                        db_game.status = "finished"
                        db_game.winner = winner
                        db_game.current_turn = None
                        if winner == "DRAW":
                            move_desc += " Game Over! It's a DRAW!"
                        else:
                            move_desc += f" Game Over! Winner: {winner}"
                    else:
                        db_game.current_turn = get_next_turn_checkers(db_player.color)
                        
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
                    asyncio.create_task(handle_bot_turns(game_id))
    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)
        asyncio.create_task(manager.broadcast(game_id, {
            "type": "system",
            "message": f"{username} has disconnected."
        }))
