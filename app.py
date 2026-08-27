from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime


app = Flask(__name__)

# Chave utilizada pelo Flask para mensagens flash
app.secret_key = "chave-secreta-cafeteria"


# ==========================================
# CONFIGURAÇÕES / REGRAS DE NEGÓCIO
# ==========================================

MIN_PESSOAS = 1
MAX_PESSOAS = 20

MIN_NOME = 3
MAX_NOME = 100

MAX_OBSERVACAO = 500

STATUS_PENDENTE = "Pendente"
STATUS_CONFIRMADA = "Confirmada"


# ==========================================
# BANCO DE DADOS EM MEMÓRIA
# ==========================================

reservas = []

# Controla o próximo ID da reserva
proximo_id = 1


# ==========================================
# ROTA - PÁGINA INICIAL
# ==========================================

@app.route("/")
def index():

    # --------------------------------------
    # MÉTRICAS DO SISTEMA
    # --------------------------------------

    total_reservas = len(reservas)

    reservas_pendentes = sum(
        1
        for reserva in reservas
        if reserva["status"] == STATUS_PENDENTE
    )

    reservas_confirmadas = sum(
        1
        for reserva in reservas
        if reserva["status"] == STATUS_CONFIRMADA
    )

    return render_template(
        "index.html",
        reservas=reservas,
        total_reservas=total_reservas,
        reservas_pendentes=reservas_pendentes,
        reservas_confirmadas=reservas_confirmadas
    )


# ==========================================
# ROTA - PÁGINA DE RESERVA
# ==========================================

@app.route("/reserva")
def reserva():
    return render_template("reserva.html")


# ==========================================
# ROTA - RECEBIMENTO DA RESERVA
# ==========================================

@app.route("/confirmacao", methods=["POST"])
def confirmacao():

    global proximo_id

    # --------------------------------------
    # RECEBENDO OS DADOS DO FORMULÁRIO
    # --------------------------------------

    nome = request.form.get("nome", "").strip()
    data = request.form.get("data", "").strip()
    horario = request.form.get("horario", "").strip()
    pessoas = request.form.get("pessoas", "").strip()
    categoria = request.form.get("categoria", "").strip()
    observacao = request.form.get("observacao", "").strip()


    # ======================================
    # VALIDAÇÃO DO NOME
    # ======================================

    if not nome:

        flash(
            "O campo nome é obrigatório.",
            "erro"
        )

        return redirect(url_for("reserva"))


    if len(nome) < MIN_NOME:

        flash(
            f"O nome deve possuir pelo menos {MIN_NOME} caracteres.",
            "erro"
        )

        return redirect(url_for("reserva"))


    if len(nome) > MAX_NOME:

        flash(
            f"O nome pode possuir no máximo {MAX_NOME} caracteres.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # VALIDAÇÃO DA DATA
    # ======================================

    if not data:

        flash(
            "A data da reserva é obrigatória.",
            "erro"
        )

        return redirect(url_for("reserva"))


    try:

        data_reserva = datetime.strptime(
            data,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "A data informada é inválida.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # Não permite reservar para uma data passada
    data_atual = datetime.now().date()

    if data_reserva < data_atual:

        flash(
            "A data da reserva não pode ser anterior à data atual.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # VALIDAÇÃO DO HORÁRIO
    # ======================================

    if not horario:

        flash(
            "O horário da reserva é obrigatório.",
            "erro"
        )

        return redirect(url_for("reserva"))


    try:

        datetime.strptime(
            horario,
            "%H:%M"
        )

    except ValueError:

        flash(
            "O horário informado é inválido.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # VALIDAÇÃO DA QUANTIDADE DE PESSOAS
    # ======================================

    if not pessoas:

        flash(
            "Informe a quantidade de pessoas.",
            "erro"
        )

        return redirect(url_for("reserva"))


    try:

        pessoas = int(pessoas)

    except ValueError:

        flash(
            "A quantidade de pessoas deve ser um número inteiro.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # Não permite zero ou números negativos
    if pessoas < MIN_PESSOAS:

        flash(
            "A quantidade de pessoas deve ser maior que zero.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # Limite máximo
    if pessoas > MAX_PESSOAS:

        flash(
            f"A reserva permite no máximo {MAX_PESSOAS} pessoas.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # VALIDAÇÃO DA CATEGORIA
    # ======================================

    categorias_validas = [
        "Café da manhã",
        "Almoço",
        "Café da tarde",
        "Jantar",
        "Comemoração",
        "Reunião"
    ]


    if not categoria:

        flash(
            "Selecione uma categoria para a reserva.",
            "erro"
        )

        return redirect(url_for("reserva"))


    if categoria not in categorias_validas:

        flash(
            "A categoria selecionada é inválida.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # VALIDAÇÃO DA OBSERVAÇÃO
    # ======================================

    if len(observacao) > MAX_OBSERVACAO:

        flash(
            f"A observação pode possuir no máximo "
            f"{MAX_OBSERVACAO} caracteres.",
            "erro"
        )

        return redirect(url_for("reserva"))


    # ======================================
    # CRIAÇÃO DA RESERVA
    # ======================================

    nova_reserva = {

        "id": proximo_id,

        "nome": nome,

        "data": data,

        "horario": horario,

        "pessoas": pessoas,

        "categoria": categoria,

        "observacao": observacao,

        "status": STATUS_PENDENTE
    }


    # ======================================
    # SALVANDO NA MEMÓRIA
    # ======================================

    reservas.append(nova_reserva)

    proximo_id += 1


    # ======================================
    # REDIRECIONANDO PARA CONFIRMAÇÃO
    # ======================================

    return render_template(
        "confirmacao.html",
        reserva=nova_reserva
    )


# ==========================================
# ROTA - LISTAGEM DE RESERVAS
# ==========================================

@app.route("/reservas")
def listar_reservas():

    # --------------------------------------
    # RECEBENDO O TERMO DE BUSCA
    # --------------------------------------

    busca = request.args.get(
        "busca",
        ""
    ).strip()


    # --------------------------------------
    # FILTRO POR NOME OU CATEGORIA
    # --------------------------------------

    if busca:

        termo_busca = busca.casefold()

        reservas_filtradas = [

            reserva

            for reserva in reservas

            if (
                termo_busca in reserva["nome"].casefold()
                or termo_busca in reserva["categoria"].casefold()
            )

        ]

    else:

        reservas_filtradas = reservas


    # --------------------------------------
    # EXIBIÇÃO DA LISTAGEM
    # --------------------------------------

    return render_template(
        "reservas.html",
        reservas=reservas_filtradas,
        busca=busca
    )


# ==========================================
# ROTA - ALTERAR STATUS
# ==========================================

@app.route(
    "/mudar-status/<int:reserva_id>",
    methods=["POST"]
)
def mudar_status(reserva_id):

    # --------------------------------------
    # PROCURANDO A RESERVA
    # --------------------------------------

    reserva_encontrada = next(

        (
            reserva
            for reserva in reservas
            if reserva["id"] == reserva_id
        ),

        None
    )


    # --------------------------------------
    # RESERVA NÃO ENCONTRADA
    # --------------------------------------

    if reserva_encontrada is None:

        flash(
            "Reserva não encontrada.",
            "erro"
        )

        return redirect(
            url_for("listar_reservas")
        )


    # --------------------------------------
    # ALTERAÇÃO DO STATUS
    # --------------------------------------

    if reserva_encontrada["status"] == STATUS_PENDENTE:

        reserva_encontrada["status"] = STATUS_CONFIRMADA

    elif reserva_encontrada["status"] == STATUS_CONFIRMADA:

        reserva_encontrada["status"] = STATUS_PENDENTE

    else:

        # Proteção contra um estado inválido
        reserva_encontrada["status"] = STATUS_PENDENTE


    # --------------------------------------
    # MENSAGEM DE SUCESSO
    # --------------------------------------

    flash(

        f'Status da reserva de '
        f'{reserva_encontrada["nome"]} '
        f'alterado para '
        f'{reserva_encontrada["status"]}.',

        "sucesso"
    )


    return redirect(
        url_for("listar_reservas")
    )


# ==========================================
# TRATAMENTO DE ERROS
# ==========================================

@app.errorhandler(404)
def pagina_nao_encontrada(error):

    return """
        <h1>Página não encontrada</h1>
        <p>A página solicitada não existe.</p>
        <a href="/">Voltar para o início</a>
    """, 404


# ==========================================
# INICIALIZAÇÃO DO SISTEMA
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )