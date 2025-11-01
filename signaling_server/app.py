# app.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import requests

st.set_page_config(page_title="Peer Interview Room", layout="wide")

SIGNALING_URL = "ws://localhost:8000/ws"  # point to your FastAPI server
STUN_SERVER = [{"urls": ["stun:stun.l.google.com:19302"]}]

st.title("🎥 Peer-to-Peer Interview Room")

room_id = st.text_input("Enter Room ID (e.g., 'test-room')")
if not room_id:
    st.info("Enter a room ID to create or join.")
    st.stop()

st.markdown("Click 'Start' to join the room and share your webcam.")

rtc_configuration = RTCConfiguration({"iceServers": STUN_SERVER})

# Each participant will call webrtc_streamer with the same key (room)
webrtc_streamer(
    key=f"room_{room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=rtc_configuration,
    media_stream_constraints={"video": True, "audio": True},
    signaling_server_url=SIGNALING_URL,
)