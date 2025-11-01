import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase

# ----- WebRTC configuration -----
RTC_CONFIG = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# ----- Simple login -----
def login():
    st.session_state["username"] = st.text_input("Enter your name:")
    st.session_state["role"] = st.selectbox("Select your role", ["Host", "Peer"])
    if st.button("Enter Room"):
        if st.session_state["username"]:
            st.session_state["entered"] = True
        else:
            st.warning("Please enter a username!")

# ----- Custom video processor for connection status -----
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.status = "Waiting for connection..."
    def recv(self, frame):
        self.status = "Connected ✅"
        return frame

# ----- Main app -----
def main():
    st.set_page_config(page_title="Paired Webcam PoC", layout="wide")
    st.title("👥 Streamlit Paired Webcam (Minimized View)")

    if "entered" not in st.session_state:
        login()
        return

    st.success(f"Welcome, {st.session_state['username']} ({st.session_state['role']})")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🎥 Peer Video (Main View)")
        peer_key = "peer_view"
        ctx_peer = webrtc_streamer(
            key=peer_key,
            mode=WebRtcMode.RECVONLY,
            rtc_configuration=RTC_CONFIG,
        )

    with col2:
        st.subheader("🧍‍♂️ Your Camera (Mini View)")
        self_key = "self_view"
        ctx_self = webrtc_streamer(
            key=self_key,
            mode=WebRtcMode.SENDONLY,
            rtc_configuration=RTC_CONFIG,
            media_stream_constraints={"video": True, "audio": True},
            video_processor_factory=VideoProcessor,
        )
        if ctx_self.video_processor:
            st.markdown(f"**Status:** {ctx_self.video_processor.status}")

    st.markdown("---")
    st.caption("⚠️ Both users must open the same app and choose opposite roles.")


if __name__ == "__main__":
    main()