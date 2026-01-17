import streamlit as st


def require_login(valid_token: str):
    if st.session_state.get('authenticated', False):
        return

    st.title('Acceso requerido')

    with st.form('login_form', clear_on_submit = False):
        token = st.text_input(
            'Token de acceso',
            type = 'password',
            placeholder = 'Ingresa el token y presiona Enter'
        )
        submitted = st.form_submit_button('Entrar')

    if submitted:
        if token == valid_token:
            st.session_state['authenticated'] = True
            st.success('Acceso concedido')
            st.rerun()
        else:
            st.error('Token incorrecto')

    st.stop()
