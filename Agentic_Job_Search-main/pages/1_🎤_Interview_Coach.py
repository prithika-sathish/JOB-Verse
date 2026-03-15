import streamlit as st
from agents.interview_coach_agent import InterviewCoachAgent
import time
import tempfile
import os
from theme import apply_dashboard_theme

# Voice mode imports (lazy load to avoid errors if not installed)
try:
    from audio_recorder_streamlit import audio_recorder
    import speech_recognition as sr
    from gtts import gTTS
    import base64
    VOICE_MODE_AVAILABLE = True
except ImportError:
    VOICE_MODE_AVAILABLE = False

st.set_page_config(page_title="Interview Coach", page_icon="🎤", layout="wide")
apply_dashboard_theme()

# Title
st.title("🎤 AI Interview Coach")
st.caption("Practice with AI-generated questions and get instant feedback")

# Initialize agent
@st.cache_resource
def get_coach():
    return InterviewCoachAgent()

coach = get_coach()

# Mode Selection (Voice vs Text)
st.divider()
col_mode1, col_mode2, col_mode3 = st.columns([1, 2, 1])

with col_mode2:
    if not VOICE_MODE_AVAILABLE:
        st.warning("⚠️ Voice mode dependencies not installed. Using text mode only.")
        interview_mode = "text"
    else:
        interview_mode = st.radio(
            "**Select Interview Mode:**",
            options=["text", "voice"],
            format_func=lambda x: "✍️ Text Mode" if x == "text" else "🎤 Voice Mode",
            horizontal=True,
            help="Text: Type your answers | Voice: Speak your answers"
        )

st.divider()

# Sidebar controls
with st.sidebar:
    st.header("Practice Settings")
    
    question_type = st.selectbox(
        "Question Type",
        ["behavioral", "technical", "situational"],
        help="Choose the type of interview questions"
    )
    
    num_questions = st.slider("Number of Questions", 1, 10, 5)
    
    st.divider()
    
    # Tips
    st.subheader("💡 Quick Tips")
    tips = coach.get_practice_tips(question_type)
    for tip in tips[:3]:
        st.info(tip, icon="✨")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="Paste the full job description for the role you're preparing for...",
        help="The AI will generate relevant questions based on this"
    )
    
    # Different buttons for different modes
    if interview_mode == "voice" and VOICE_MODE_AVAILABLE:
        if st.button("🎤 Start Live Interview", type="primary", use_container_width=True):
            if not job_description:
                st.error("Please provide a job description first!")
            else:
                with st.spinner("Preparing your live interview..."):
                    # Generate questions
                    questions = coach.generate_questions(job_description, question_type, num_questions)
                    
                    # Initialize live interview session
                    st.session_state.questions = questions
                    st.session_state.question_type = question_type
                    st.session_state.job_description = job_description
                    st.session_state.interview_active = True
                    st.session_state.current_question = 0
                    st.session_state.conversation_log = []
                    st.session_state.interview_start_time = time.time()
                    
                    st.success(f"🎙️ Live interview ready! {len(questions)} questions prepared.")
                    st.rerun()
    else:
        # Text mode: original button
        if st.button("🚀 Generate Questions", type="primary", use_container_width=True):
            if not job_description:
                st.error("Please provide a job description first!")
            else:
                with st.spinner("Generating personalized interview questions..."):
                    # Generate new questions with current settings
                    questions = coach.generate_questions(job_description, question_type, num_questions)
                    
                    # Store everything in session state
                    st.session_state.questions = questions
                    st.session_state.question_type = question_type
                    st.session_state.num_questions = num_questions
                    st.session_state.job_description = job_description
                    st.session_state.current_question = 0
                    st.session_state.answers = {}
                    st.session_state.interview_active = False
                    
                    st.success(f"Generated {len(questions)} {question_type} questions!")
                    st.rerun()

with col2:
    st.subheader("🎯 Practice Session")
    
    # LIVE INTERVIEW MODE (Voice)
    if interview_mode == "voice" and st.session_state.get('interview_active', False) and VOICE_MODE_AVAILABLE:
        questions = st.session_state.questions
        current_q = st.session_state.get('current_question', 0)
        
        # Interview header (removed elapsed timer - only show in recording)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; border-radius:12px; margin-bottom:20px; color:white;">
            <h2 style="margin:0; font-size:1.5rem;">🎤 LIVE INTERVIEW IN PROGRESS</h2>
            <p style="margin:8px 0 0 0; opacity:0.9; font-size:1.1rem;">Question {current_q + 1} of {len(questions)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress((current_q + 1) / len(questions))
        
        # Check if interview complete
        if current_q >= len(questions):
            st.success("✅ Interview Complete!")
            st.balloons()
            
            # Show full transcript
            st.subheader("📝 Interview Transcript")
            for i, entry in enumerate(st.session_state.get('conversation_log', []), 1):
                with st.container():
                    st.markdown(f"**Q{i}:** {entry['question']}")
                    st.info(f"💬 **Your Answer:** {entry['answer']}")
                    st.write("")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Start New Interview", use_container_width=True):
                    st.session_state.interview_active = False
                    st.session_state.conversation_log = []
                    st.session_state.current_question = 0
                    st.rerun()
            with col2:
                if st.button("📊 View Feedback", use_container_width=True):
                    st.info("Detailed feedback feature coming soon!")
        
        else:
            # Current question
            current_question = questions[current_q]
            
            # Question display
            st.markdown(f"""
            <div style="background:#f8fafc; padding:20px; border-radius:10px; border-left:5px solid #667eea; margin:20px 0;">
                <p style="margin:0; color:#94a3b8; font-size:0.9rem; font-weight:600;">QUESTION {current_q + 1}</p>
                <h3 style="margin:10px 0 0 0; color:#1e293b; line-height:1.5;">{current_question}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize recording state
            if f'recording_state_{current_q}' not in st.session_state:
                st.session_state[f'recording_state_{current_q}'] = 'tts_pending'
            
            recording_state = st.session_state[f'recording_state_{current_q}']
            
            # PHASE 1: Play TTS
            if recording_state == 'tts_pending':
                st.markdown("**🗣️ AI Recruiter is speaking...**")
                st.info(f"Question: {current_question}")
                
                try:
                    with st.spinner("AI speaking question..."):
                        tts = gTTS(text=f"Question {current_q + 1}. {current_question}", lang='en', slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                            tts_file_path = fp.name
                            tts.save(tts_file_path)
                        
                        # Read and encode audio
                        with open(tts_file_path, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                            audio_b64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # Try to clean up, but don't fail if file is locked
                        try:
                            os.unlink(tts_file_path)
                        except Exception:
                            pass  # File will be cleaned up by OS temp cleanup
                    
                    # Better timing calculation 
                    estimated_duration = max(3, len(current_question) / 12 + 2)  # More generous timing
                    
                    st.info(f"⏳ Waiting for AI to finish speaking... (~{int(estimated_duration)}s)")
                    
                    # Wait for TTS to finish
                    time.sleep(min(estimated_duration, 15))
                    
                    # Move to recording phase
                    st.session_state[f'recording_state_{current_q}'] = 'recording'
                    st.session_state[f'recording_start_{current_q}'] = time.time()
                    st.rerun()
                        
                except Exception as e:
                    st.error(f"TTS Error: {str(e)}")
                    st.session_state[f'recording_state_{current_q}'] = 'recording'
                    st.session_state[f'recording_start_{current_q}'] = time.time()
                    st.rerun()
            
            # PHASE 2: Auto-record with 30-second timer
            elif recording_state == 'recording':
                # Calculate remaining time
                start_time = st.session_state.get(f'recording_start_{current_q}', time.time())
                elapsed_rec = time.time() - start_time
                remaining = max(0, 30 - int(elapsed_rec))
                
                # Check if 30 seconds elapsed - AUTO SKIP
                if elapsed_rec >= 30:
                    st.warning("⏰ Time's up! Moving to next question...")
                    
                    # Check if we have recorded audio
                    if f'recorded_audio_{current_q}' in st.session_state:
                        # Process what we have
                        st.session_state[f'recording_state_{current_q}'] = 'transcribing'
                    else:
                        # No audio, skip to next
                        st.session_state.conversation_log.append({
                            'question': current_question,
                            'answer': "[No answer provided - timeout]"
                        })
                        st.session_state.current_question = current_q + 1
                    
                    time.sleep(1)
                    st.rerun()
                
                # Big countdown timer
                timer_color = "#10b981" if remaining > 10 else "#f59e0b" if remaining > 5 else "#ef4444"
                st.markdown(f"""
                <div style="background:{timer_color}20; padding:30px; border-radius:15px; text-align:center; margin:20px 0; border:3px solid {timer_color};">
                    <p style="margin:0; color:#64748b; font-size:1rem; font-weight:600;">⏱️ TIME REMAINING</p>
                    <h1 style="margin:10px 0 5px 0; color:{timer_color}; font-size:4rem; font-weight:bold;">{remaining}s</h1>
                    <p style="margin:0; color:{timer_color}; font-size:1.3rem; font-weight:600;">🎙️ SPEAK YOUR ANSWER NOW</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-recording indicator
                st.markdown("""
                <div style="text-align:center; margin:20px 0;">
                    <div style="display:inline-block; background:#ef4444; width:24px; height:24px; border-radius:50%; animation:pulse 1.5s infinite;"></div>
                    <p style="margin:10px 0 0 0; color:#ef4444; font-weight:700; font-size:1.3rem;">● RECORDING LIVE</p>
                    <p style="margin:5px 0 0 0; color:#64748b; font-size:0.95rem;">Click the microphone below to start recording, then speak</p>
                </div>
                <style>
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(1.2); }
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Hidden audio recorder (auto-activated by browser)
                audio_bytes = audio_recorder(
                    text="",
                    recording_color="#ef4444",
                    neutral_color="#3b82f6",
                    icon_name="microphone",
                    icon_size="6x",
                    key=f"auto_recorder_{current_q}"
                )
                
                # Check if user finished recording
                if audio_bytes:
                    st.session_state[f'recorded_audio_{current_q}'] = audio_bytes
                    st.session_state[f'recording_state_{current_q}'] = 'transcribing'
                    st.rerun()
                
                # Auto-refresh to update timer every second
                time.sleep(1)
                st.rerun()
            
            # PHASE 3: Transcribe
            elif recording_state == 'transcribing':
                audio_bytes = st.session_state.get(f'recorded_audio_{current_q}')
                
                st.info("🔄 Transcribing your answer...")
                
                # Save audio file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                    fp.write(audio_bytes)
                    audio_file_path = fp.name
                
                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(audio_file_path) as source:
                        audio_data = recognizer.record(source)
                        answer_text = recognizer.recognize_google(audio_data)
                        
                        # Save to log
                        st.session_state.conversation_log.append({
                            'question': current_question,
                            'answer': answer_text
                        })
                        
                        st.success(f"✅ Transcribed: \"{answer_text[:80]}...\"")
                        
                        # Move to feedback phase
                        st.session_state[f'recording_state_{current_q}'] = 'ai_feedback'
                        st.session_state[f'answer_text_{current_q}'] = answer_text
                        st.rerun()
                        
                except sr.UnknownValueError:
                    st.error("❌ Could not understand audio. Moving to next question...")
                    st.session_state.conversation_log.append({
                        'question': current_question,
                        'answer': "[Audio unclear]"
                    })
                    time.sleep(1.5)
                    st.session_state.current_question = current_q + 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    os.unlink(audio_file_path)
            
            # PHASE 5: AI Feedback (NEW!)
            elif recording_state == 'ai_feedback':
                answer_text = st.session_state.get(f'answer_text_{current_q}', '')
                
                st.markdown("**🤖 AI Recruiter responding...**")
                
                try:
                    # Quick evaluation
                    with st.spinner("Analyzing your answer..."):
                        evaluation = coach.evaluate_answer(current_question, answer_text, st.session_state.job_description)
                        score = evaluation.get('score', 5)
                        
                        # Generate conversational feedback
                        if score >= 8:
                            feedback_text = "Excellent answer! That's exactly what we're looking for."
                        elif score >= 6:
                            feedback_text = "Good response. I like how you explained that."
                        elif score >= 4:
                            feedback_text = "Okay, I understand. You might want to elaborate more on that in future interviews."
                        else:
                            feedback_text = "I see. Let me note that down."
                        
                        # Add transition to next question
                        if current_q < len(questions) - 1:
                            feedback_text += f" Let's move on. Your next question is number {current_q + 2}."
                        else:
                            feedback_text += " That completes our interview. Thank you!"
                        
                        # Speak feedback via TTS
                        st.info(f"💬 AI: \"{feedback_text}\"")
                        
                        tts_feedback = gTTS(text=feedback_text, lang='en', slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                            feedback_file_path = fp.name
                            tts_feedback.save(feedback_file_path)
                        
                        # Read and encode feedback audio
                        with open(feedback_file_path, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                            audio_b64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                        
                        # Try to clean up, but don't fail if file is locked
                        try:
                            os.unlink(feedback_file_path)
                        except Exception:
                            pass  # File will be cleaned up by OS temp cleanup
                        
                        # Wait for feedback TTS to finish
                        feedback_duration = len(feedback_text) / 15  # ~15 chars per second
                        time.sleep(min(feedback_duration + 1, 8))
                        
                        # Store evaluation and move to next question
                        st.session_state.conversation_log[-1]['evaluation'] = evaluation
                        st.session_state.conversation_log[-1]['feedback'] = feedback_text
                        st.session_state.current_question = current_q + 1
                        st.rerun()
                        
                except Exception as e:
                    st.warning(f"Feedback error: {str(e)}")
                    # Skip feedback, just move on
                    time.sleep(1)
                    st.session_state.current_question = current_q + 1
                    st.rerun()
            
            # Conversation history
            st.write("")
            if st.session_state.get('conversation_log'):
                with st.expander(f"📜 Previous Answers ({len(st.session_state.conversation_log)})", expanded=False):
                    for i, entry in enumerate(st.session_state.conversation_log, 1):
                        st.markdown(f"**Q{i}:** {entry['question']}")
                        st.caption(f"💬 {entry['answer']}")
                        st.divider()
            
            # Emergency controls
            st.write("")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⏹️ End Interview", type="secondary", use_container_width=True):
                    st.session_state.interview_active = False
                    st.rerun()
            with col_b:
                if st.button("⏭️ Skip This Question", type="secondary", use_container_width=True):
                    st.session_state.current_question = current_q + 1
                    st.rerun()
    
    # TEXT MODE or NO ACTIVE INTERVIEW (original behavior)
    elif 'questions' in st.session_state and st.session_state.questions:
        questions = st.session_state.questions
        current_q = st.session_state.get('current_question', 0)
        
        # Interview header with timer
        elapsed = int(time.time() - st.session_state.get('interview_start_time', time.time()))
        mins, secs = divmod(elapsed, 60)
        
        st.markdown(f"""
        <div style="background:#3b82f6;20; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h3 style="margin:0; color:#3b82f6;">🎤 LIVE INTERVIEW IN PROGRESS</h3>
            <p style="margin:5px 0 0 0; color:#64748b;">⏱️ {mins:02d}:{secs:02d} | Question {current_q + 1} of {len(questions)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress
        st.progress((current_q + 1) / len(questions))
        
        # Check if interview complete
        if current_q >= len(questions):
            st.success("✅ Interview Complete!")
            st.balloons()
            
            # Show conversation log
            st.subheader("📝 Interview Transcript")
            for i, entry in enumerate(st.session_state.get('conversation_log', []), 1):
                st.markdown(f"**Q{i}:** {entry['question']}")
                st.info(f"**Your Answer:** {entry['answer']}")
            
            if st.button("🔄 Start New Interview"):
                st.session_state.interview_active = False
                st.session_state.conversation_log = []
                st.session_state.current_question = 0
                st.rerun()
        else:
            # Current question
            current_question = questions[current_q]
            
            st.markdown(f"""
            <div style="background:#f8fafc; padding:15px; border-radius:8px; border-left:4px solid #3b82f6; margin:15px 0;">
                <p style="margin:0; color:#64748b; font-size:0.85rem;">QUESTION {current_q + 1}</p>
                <h4 style="margin:5px 0 0 0; color:#0f172a;">{current_question}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-play question audio (TTS)
            if f'tts_played_{current_q}' not in st.session_state:
                try:
                    with st.spinner("🗣️ AI speaking..."):
                        tts = gTTS(text=f"Question {current_q + 1}. {current_question}", lang='en', slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                            tts.save(fp.name)
                            with open(fp.name, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                                audio_b64 = base64.b64encode(audio_bytes).decode()
                                audio_html = f"""
                                <audio autoplay>
                                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                                </audio>
                                """
                                st.markdown(audio_html, unsafe_allow_html=True)
                            os.unlink(fp.name)
                    st.session_state[f'tts_played_{current_q}'] = True
                    time.sleep(2)  # Give time for audio to play
                except Exception as e:
                    st.warning(f"Could not play audio: {str(e)}")
            
            # Audio recorder for answer
            st.markdown("**🎙️ Your Answer (speak now):**")
            st.info("Click the microphone to start recording your answer")
            
            audio_bytes = audio_recorder(
                text="",
                recording_color="#ef4444",
                neutral_color="#3b82f6",
                icon_name="microphone",
                icon_size="3x",
                key=f"recorder_{current_q}"
            )
            
            # Process recorded answer
            if audio_bytes and f'answer_processed_{current_q}' not in st.session_state:
                st.success("✅ Recording captured! Transcribing...")
                
                # Save and transcribe
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                    fp.write(audio_bytes)
                    audio_file_path = fp.name
                
                try:
                    with st.spinner("🔄 Transcribing your answer..."):
                        recognizer = sr.Recognizer()
                        with sr.AudioFile(audio_file_path) as source:
                            audio_data = recognizer.record(source)
                            answer_text = recognizer.recognize_google(audio_data)
                            
                            # Save to conversation log
                            st.session_state.conversation_log.append({
                                'question': current_question,
                                'answer': answer_text
                            })
                            
                            st.session_state[f'answer_processed_{current_q}'] = True
                            st.success(f"📝 Got it: \"{answer_text[:100]}...\"")
                            
                            # Auto-advance to next question
                            time.sleep(1)
                            st.session_state.current_question = current_q + 1
                            st.rerun()
                            
                except sr.UnknownValueError:
                    st.error("❌ Could not understand. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    os.unlink(audio_file_path)
            
            # Show conversation history
            if st.session_state.get('conversation_log'):
                with st.expander("📜 Conversation History", expanded=False):
                    for i, entry in enumerate(st.session_state.conversation_log, 1):
                        st.markdown(f"**Q{i}:** {entry['question']}")
                        st.caption(f"**A:** {entry['answer']}")
                        st.write("")
            
            # Control buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("⏹️ End Interview", use_container_width=True):
                    st.session_state.interview_active = False
                    st.rerun()
            with col_b:
                if st.button("⏭️ Skip Question", use_container_width=True):
                    st.session_state.current_question = current_q + 1
                    st.rerun()
    
    # TEXT MODE or NO ACTIVE INTERVIEW (original behavior)
    elif 'questions' in st.session_state and st.session_state.questions:
        questions = st.session_state.questions
        current_q = st.session_state.get('current_question', 0)
        
        # Show current session info
        session_type = st.session_state.get('question_type', 'behavioral')
        mode_icon = "🎤" if interview_mode == "voice" else "✍️"
        st.info(f"{mode_icon} **Current Session:** {len(questions)} {session_type.title()} questions ({interview_mode.title()} Mode)", icon="ℹ️")
        
        # Progress
        st.progress((current_q + 1) / len(questions), text=f"Question {current_q + 1} of {len(questions)}")
        
        # Display current question
        st.markdown(f"### Question {current_q + 1}")
        st.markdown(f"**{questions[current_q]}**")
        
        # VOICE MODE
        if interview_mode == "voice" and VOICE_MODE_AVAILABLE:
            st.write("")
            
            # Auto-play question audio (TTS)
            if f'audio_played_{current_q}' not in st.session_state:
                try:
                    tts = gTTS(text=questions[current_q], lang='en', slow=False)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        with open(fp.name, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                            audio_b64 = base64.b64encode(audio_bytes).decode()
                            audio_html = f"""
                            <audio autoplay>
                                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                            </audio>
                            """
                            st.markdown(audio_html, unsafe_allow_html=True)
                        os.unlink(fp.name)
                        st.session_state[f'audio_played_{current_q}'] = True
                except Exception as e:
                    st.warning(f"Could not play audio: {str(e)}")
            
            # Audio recorder
            st.markdown("**🎙️ Record Your Answer:**")
            audio_bytes = audio_recorder(
                text="Click to record",
                recording_color="#e74c3c",
                neutral_color="#6c757d",
                icon_name="microphone",
                icon_size="2x"
            )
            
            # Transcribe audio
            answer_text = ""
            if audio_bytes:
                st.success("✅ Recording captured!")
                
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
                    fp.write(audio_bytes)
                    audio_file_path = fp.name
                
                try:
                    # Speech to text
                    with st.spinner("🔄 Transcribing your answer..."):
                        recognizer = sr.Recognizer()
                        with sr.AudioFile(audio_file_path) as source:
                            audio_data = recognizer.record(source)
                            answer_text = recognizer.recognize_google(audio_data)
                            st.success(f"📝 Transcribed: \"{answer_text}\"")
                            st.session_state[f'voice_answer_{current_q}'] = answer_text
                except sr.UnknownValueError:
                    st.error("❌ Could not understand audio. Please speak clearly and try again.")
                except sr.RequestError:
                    st.error("❌ Speech recognition service unavailable. Check internet connection.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    os.unlink(audio_file_path)
            
            # Show transcribed answer
            if f'voice_answer_{current_q}' in st.session_state:
                st.markdown("**Your Transcribed Answer:**")
                st.info(st.session_state[f'voice_answer_{current_q}'])
                answer_text = st.session_state[f'voice_answer_{current_q}']
            else:
                answer_text = ""
        
        # TEXT MODE (original)
        else:
            answer_key = f"answer_{current_q}"
            answer_text = st.text_area(
                "Your Answer",
                height=150,
                key=answer_key,
                placeholder="Type your answer here... Use the STAR method if applicable."
            )
        
        # Navigation and submit buttons
        col_a, col_b, col_c = st.columns([1, 1, 1])
        
        with col_a:
            if current_q > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question = current_q - 1
                    st.rerun()
        
        with col_b:
            if st.button("✅ Evaluate Answer", type="primary", use_container_width=True):
                if not answer_text or not answer_text.strip():
                    st.error("Please provide an answer first!")
                else:
                    with st.spinner("Analyzing your answer..."):
                        evaluation = coach.evaluate_answer(questions[current_q], answer_text, job_description)
                        st.session_state.answers[current_q] = {
                            "answer": answer_text,
                            "evaluation": evaluation
                        }
                        st.rerun()
        
        with col_c:
            if current_q < len(questions) - 1:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.current_question = current_q + 1
                    st.rerun()
        
        # Show evaluation if exists
        if current_q in st.session_state.get('answers', {}):
            st.divider()
            eval_data = st.session_state.answers[current_q]["evaluation"]
            
            # Correctness indicator
            is_correct = eval_data.get("is_correct", "unknown")
            if is_correct == "correct":
                st.success("✅ **Answer is CORRECT!**", icon="✅")
            elif is_correct == "incorrect":
                st.error("❌ **Answer is INCORRECT**", icon="❌")
            elif is_correct == "partial":
                st.warning("⚠️ **Answer is PARTIALLY CORRECT**", icon="⚠️")
            elif is_correct == "error":
                st.error("⚠️ **Evaluation Error - See details below**", icon="⚠️")
            
            # Score card
            score = eval_data["score"]
            score_color = "#10b981" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
            
            st.markdown(f"""
            <div style="background:{score_color}20; padding:15px; border-radius:10px; border-left:4px solid {score_color};">
                <h3 style="margin:0; color:{score_color};">Score: {score}/10</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Detailed Feedback:**")
            st.write(eval_data["feedback"])
            
            # Show better answer if available
            better_answer = eval_data.get("better_answer", "").strip()
            if better_answer and is_correct in ["incorrect", "partial"]:
                st.divider()
                st.markdown("### 💡 Better Answer / Correction")
                st.info(better_answer)
            
            details = eval_data.get("detailed_analysis", {})
            if details.get("strengths"):
                st.success("**Strengths:**\n" + "\n".join(f"• {s}" for s in details["strengths"]))
            if details.get("improvements"):
                st.warning("**Areas to Improve:**\n" + "\n".join(f"• {i}" for i in details["improvements"]))
        
    else:
        st.info("👈 Enter a job description and click 'Generate Questions' to start practicing!", icon="ℹ️")

# Session summary
if 'answers' in st.session_state and st.session_state.answers:
    st.divider()
    st.subheader("📊 Session Summary")
    
    total_questions = len(st.session_state.get('questions', []))
    answered = len(st.session_state.answers)
    
    if answered > 0:
        avg_score = sum(a["evaluation"]["score"] for a in st.session_state.answers.values()) / answered
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Answered", f"{answered}/{total_questions}")
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}/10")
        with col3:
            completion = (answered / total_questions) * 100
            st.metric("Completion", f"{completion:.0f}%")
