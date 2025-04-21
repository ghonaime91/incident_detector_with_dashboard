from flask_socketio import  (
    emit,
    join_room,
    leave_room
)
from app import socketio
from flask import request



# Dictionary to store information about call rooms 
rooms = {}

# SocketIO event handler for when a client connects
@socketio.on('connect')
def handle_connect():
    """Handles the event when a client connects to the SocketIO server."""
    print(f"Client connected: {request.sid}")
    # Optionally, you can emit an event to the client upon connection


# SocketIO event handler for when a client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    """Handles the event when a client disconnects from the SocketIO server."""
    print(f"Client disconnected: {request.sid}")
    # Clean up rooms the client was in
    for room_id, sids in list(rooms.items()):
        if request.sid in sids:
            rooms[room_id].remove(request.sid)
            if not rooms[room_id]:
                del rooms[room_id]
            emit('call_ended', to=room_id) # Notify other clients in the room
            print(f"Client {request.sid} left room {room_id}. Room now: {rooms.get(room_id)}")


# SocketIO event handler for a client joining a call room
@socketio.on('join_call_room')
def handle_join_call_room(room_id):
    """Handles the event when a client joins a specific call room."""
    join_room(room_id)
    print(f"Client {request.sid} joined room {room_id}")
    if room_id not in rooms:
        rooms[room_id] = []
    if request.sid not in rooms[room_id]:
        rooms[room_id].append(request.sid)
    print(f"Room {room_id} now contains: {rooms[room_id]}")


# SocketIO event handler for a client leaving a call room
@socketio.on('leave_call_room')
def handle_leave_call_room(room_id):
    """Handles the event when a client leaves a specific call room."""
    leave_room(room_id)
    print(f"Client {request.sid} left room {room_id}")
    if room_id in rooms and request.sid in rooms[room_id]:
        rooms[room_id].remove(request.sid)
        if not rooms[room_id]:
            del rooms[room_id]
        print(f"Room {room_id} now contains: {rooms.get(room_id)}")


# SocketIO event handler for receiving an 'offer' (session description) from a peer
@socketio.on('offer')
def handle_offer(data):
    """Handles the 'offer' event, broadcasting it to others in the same room."""
    print("Received offer from", request.sid, ":", data)
    room_id = data.get('room_id')
    if room_id and room_id in rooms:
        # Send the offer to all other clients in the room
        emit('offer', data, to=room_id, include_self=False)
    else:
        print("Error: No valid room_id provided in offer")


# SocketIO event handler for receiving an 'answer' (session description) from a peer
@socketio.on('answer')
def handle_answer(data):
    """Handles the 'answer' event, broadcasting it to others in the same room."""
    print("Received answer from", request.sid, ":", data)
    room_id = data.get('room_id')
    if room_id and room_id in rooms:
        # Send the answer to all other clients in the room
        emit('answer', data, to=room_id, include_self=False)
    else:
        print("Error: No valid room_id provided in answer")


# SocketIO event handler for receiving an 'ice-candidate' (for NAT traversal) from a peer
@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    """Handles the 'ice-candidate' event, broadcasting it to others in the same room."""
    print("Received ICE candidate from", request.sid, ":", data)
    room_id = data.get('room_id')
    if room_id and room_id in rooms:
        # Send the ICE candidate to all other clients in the room
        emit('ice-candidate', data, to=room_id, include_self=False)
    else:
        print("Error: No valid room_id provided in ICE candidate")


# SocketIO event handler for when a client ends a call
@socketio.on('end_call')
def handle_end_call(room_id):
    """Handles the 'end_call' event, notifying others in the room that the call has ended."""
    print(f"Call ended by {request.sid} in room {room_id}")
    if room_id and room_id in rooms:
        emit('call_ended', to=room_id, include_self=False) # Notify others
        if request.sid in rooms[room_id]:
            rooms[room_id].remove(request.sid)
            if not rooms[room_id]:
                del rooms[room_id]


