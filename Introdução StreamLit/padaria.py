import streamlit as st
import pandas as pd


st.title("Padaria Pão Quentinho")
st.write("______________________________________________")
st.header("Faça seu pedido")
st.subheader("Escolha os produtos e veja o valor total")


precos = {
    "Pão francês": 1.00,
    "Pão de queijo": 3.50,
    "Croissant": 6.00,
    "Fatia de bolo": 5.00,
    "Sonho": 4.50,
    "Café": 3.00,
    "Suco": 5.00,
}

cardapio = pd.DataFrame({
    "Produto": list(precos.keys()),
    "Preço por unidade": [f"R$ {valor:.2f}" for valor in precos.values()],
})

ver_cardapio = st.button("Ver cardápio")
if ver_cardapio:
    st.write(cardapio)

st.write("______________________________________________")

cliente = st.text_input("Qual é o seu nome?")
if cliente:
    st.write("Olá,", cliente)


itens = st.multiselect("Escolha os itens do pedido:", list(precos.keys()))
st.write("Você selecionou:", itens)

st.write("______________________________________________")


with st.form("pedido_padaria"):
    quantidades = {}

    for item in itens:
        quantidades[item] = st.number_input(
            f"Quantidade de {item}:",
            min_value=1,
            value=1,
            step=1,
        )

    pagamento = st.selectbox(
        "Forma de pagamento:",
        ["Dinheiro", "Pix", "Cartão"],
    )

    calcular = st.form_submit_button("Calcular total")


coluna_pedido, coluna_total = st.columns([2, 1])

if calcular:
    if itens:
        total = 0
        resumo = []

        for item in itens:
            quantidade = quantidades[item]
            subtotal = precos[item] * quantidade
            total = total + subtotal

            resumo.append({
                "Produto": item,
                "Quantidade": quantidade,
                "Subtotal": f"R$ {subtotal:.2f}",
            })

        with coluna_pedido:
            st.subheader("Resumo do pedido")
            st.write(pd.DataFrame(resumo))
            if cliente:
                st.write("Cliente:", cliente)
            st.write("Forma de pagamento:", pagamento)

        with coluna_total:
            st.subheader("Total a pagar")
            st.title(f"R$ {total:.2f}")
    else:
        st.write("Selecione pelo menos um item para calcular o total.")
