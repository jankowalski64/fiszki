import streamlit as st
import pypdf
import random

# Konfiguracja strony
st.set_page_config(
    page_title="Darmowy Generator Fisek i Notatek",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Generator Fisek i Notatek z Pliku")
st.write("Wrzuć plik PDF lub TXT z notatkami, a aplikacja wygeneruje z niego materiał do powtórek.")

# Sekcja wgrania pliku (teraz przyjmuje też .txt!)
uploaded_file = st.file_uploader("Wybierz plik", type=["pdf", "txt"])

if uploaded_file is not None:
    @st.cache_data
    def extract_text(file, file_name):
        text = ""
        if file_name.endswith('.pdf'):
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            # Obsługa pliku tekstowego TXT
            text = file.getvalue().decode("utf-8")
        return text

    with st.spinner("Przetwarzam plik..."):
        raw_text = extract_text(uploaded_file, uploaded_file.name)

    st.success(f"Pomyślnie wczytano plik! Liczba znaków: {len(raw_text)}")

    # Proste generowanie fiszek na podstawie zdań/akapitu
    if st.button("Generuj fiszki do nauki"):
        lines = [line.strip() for line in raw_text.split('\n') if len(line.strip()) > 30]
        
        if len(lines) < 2:
            st.warning("Tekst jest zbyt krótki lub ma niestandardowy format, aby utworzyć fiszki. Dodaj dłuższe zdania.")
        else:
            flashcards = []
            for i, line in enumerate(lines[:30]):
                words = line.split()
                if len(words) > 5:
                    idx = random.randint(1, len(words) - 2)
                    hidden_word = words[idx]
                    words[idx] = "_____"
                    question = " ".join(words)
                    flashcards.append({"question": question, "answer": hidden_word})
            
            st.session_state["flashcards"] = flashcards
            st.session_state["card_index"] = 0

    # Wyświetlanie fiszek, jeśli zostały wygenerowane
    if "flashcards" in st.session_state and st.session_state["flashcards"]:
        flashcards = st.session_state["flashcards"]
        idx = st.session_state["card_index"]
        
        st.markdown("---")
        st.subheader(f"Fiszka {idx + 1} z {len(flashcards)}")
        
        st.info(f"**Uzupełnij luki / Odpowiedz:**\n\n{flashcards[idx]['question']}")
        
        if "show_answer" not in st.session_state:
            st.session_state["show_answer"] = False

        if st.button("Pokaż odpowiedź"):
            st.session_state["show_answer"] = True

        if st.session_state["show_answer"]:
            st.success(f"**Odpowiedź:** {flashcards[idx]['answer']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Poprzednia") and idx > 0:
                st.session_state["card_index"] -= 1
                st.session_state["show_answer"] = False
                st.rerun()
        with col2:
            if st.button("Następna ➡️") and idx < len(flashcards) - 1:
                st.session_state["card_index"] += 1
                st.session_state["show_answer"] = False
                st.rerun()
