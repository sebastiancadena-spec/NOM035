import streamlit as st


def require_login(valid_token: str):
    if 'is_authed' not in st.session_state:
        st.session_state['is_authed'] = False

    if st.session_state['is_authed']:
        return True

    st.title('NOM-035 | Reportes')
    st.info('Ingresa el token para continuar.')

    token = st.text_input('Token', type = 'password')

    if st.button('Entrar'):
        if token == valid_token:
            st.session_state['is_authed'] = True
            st.rerun()
        else:
            st.error('Token incorrecto.')

    st.stop()
