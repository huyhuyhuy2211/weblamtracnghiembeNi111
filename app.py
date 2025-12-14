import streamlit as st
import PyPDF2
import google.generativeai as genai
import json

# --- CẤU HÌNH ---
# Dán cứng API Key của bạn vào giữa 2 dấu ngoặc kép bên dưới
# LƯU Ý QUAN TRỌNG: Không đưa code này cho người lạ, họ sẽ dùng trộm tiền/quota của bạn.
MY_SECRET_KEY = "AIzaSyC1oAIX5auNkQuq7mvd-2XD_-Szef8gUJ4" 

# Cấu hình giao diện
st.set_page_config(page_title="Web Ôn Tập Online", layout="wide")
st.title("🚀 Web Ôn Tập & Tạo Đề Thi Trực Tuyến")

# --- CÁC HÀM XỬ LÝ (Giữ nguyên) ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except:
        return ""

def generate_quiz(text):
    # Sử dụng Key đã lưu cứng
    genai.configure(api_key=MY_SECRET_KEY)
    
    generation_config = {
        "temperature": 1,
        "response_mime_type": "application/json",
    }

    # Danh sách model (Dùng 2.5 Flash như đã test thành công)
    available_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    for model_name in available_models:
        try:
            model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
            prompt = f"""
            Tạo bộ câu hỏi trắc nghiệm từ văn bản sau (Tự giải nếu không có đáp án).
            Văn bản: "{text[:30000]}"
            Trả về JSON list: [{{ "question": "...", "options": ["A...", "B..."], "answer": "A..." }}]
            """
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except:
            continue
    return []

# --- GIAO DIỆN ---
if 'quiz_data' not in st.session_state:
    st.info("👋 Chào mừng! Hãy tải tài liệu ôn tập lên để bắt đầu.")
    uploaded_file = st.file_uploader("Chọn file PDF...", type=['pdf'])
    
    if uploaded_file:
        if st.button("🚀 Tạo Đề Thi Ngay"):
            with st.spinner("Đang khởi tạo đề thi..."):
                text = extract_text_from_pdf(uploaded_file)
                data = generate_quiz(text)
                if data:
                    st.session_state['quiz_data'] = data
                    st.rerun()

elif 'quiz_data' in st.session_state:
    st.success("✅ Đề thi đã sẵn sàng!")
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Làm đề khác"):
            st.session_state.clear()
            st.rerun()

    with st.expander("Xem/Chỉnh sửa đáp án gốc (Dành cho Admin)"):
        edited_data = st.data_editor(st.session_state['quiz_data'], num_rows="dynamic")
        if st.button("Lưu chỉnh sửa"):
            st.session_state['quiz_data'] = edited_data
            st.rerun()
            
    st.divider()
    for i, q in enumerate(st.session_state['quiz_data']):
        st.subheader(f"Câu {i+1}: {q['question']}")
        ans = st.radio("Chọn:", q['options'], key=f"q{i}", index=None)
        if ans:
            if ans.split('.')[0] == q['answer'].split('.')[0]:
                st.success("Chính xác!")
            else:
                st.error(f"Sai! Đáp án là: {q['answer']}")
        st.write("---")