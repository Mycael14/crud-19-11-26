from datetime import datetime
from decimal import Decimal, InvalidOperation

import mysql.connector
from mysql.connector import errorcode

from alunos_crud import AlunosCRUD


# ======================================================================
# Funções auxiliares de entrada de dados
# ======================================================================
def ler_texto(mensagem, tamanho_max, obrigatorio=False):
    while True:
        texto = input(mensagem).strip()
        if not texto and obrigatorio:
            print("Campo obrigatório.")
        elif len(texto) > tamanho_max:
            print(f"Máximo de {tamanho_max} caracteres.")
        else:
            return texto or None


def ler_inteiro(mensagem, opcional=False):
    while True:
        texto = input(mensagem).strip()
        if not texto and opcional:
            return None
        try:
            return int(texto)
        except ValueError:
            print("Digite um número inteiro válido.")


def ler_decimal(mensagem, maximo):
    while True:
        texto = input(mensagem).strip().replace(",", ".")
        if not texto:
            return None
        try:
            numero = Decimal(texto)
        except InvalidOperation:
            print("Digite um número válido.")
            continue
        if not numero.is_finite() or not 0 < numero <= maximo:
            print(f"O valor deve ser maior que 0 e no máximo {maximo}.")
        else:
            return numero


def ler_data(mensagem):
    while True:
        texto = input(mensagem).strip()
        if not texto:
            return None
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida. Use o formato DD/MM/AAAA.")


def ler_sexo():
    while True:
        sexo = input("Sexo (M/F) [Enter para pular]: ").strip().upper()
        if sexo in ("", "M", "F"):
            return sexo or None
        print("Digite M ou F.")


def confirmar(mensagem):
    return input(mensagem).strip().lower() in ("s", "sim")


def escolher_criterio():
    """Pergunta se a operação será feita por ID ou por Nome.
    Retorna (campo, valor) ou (None, None) se a opção for inválida."""
    print("Critério: 1 - ID | 2 - Nome")
    opcao = input("Escolha: ").strip()
    if opcao == "1":
        return "id", ler_inteiro("ID do aluno: ")
    if opcao == "2":
        return "nome", ler_texto("Nome do aluno (exato): ", 30, obrigatorio=True)
    print("Opção inválida.")
    return None, None


# ======================================================================
# Exibição
# ======================================================================
def exibir_alunos(alunos):
    if not alunos:
        print("Nenhum aluno encontrado.")
        return
    print(f"\n{'ID':<4} {'Nome':<26} {'Profissão':<21} {'Nascimento':<11} "
          f"{'Sexo':<5} {'Peso':>7} {'Altura':>6}  {'Nacionalidade':<14} {'Curso':>5}")
    print("-" * 110)
    for (id_, nome, profissao, nascimento, sexo, peso, altura,
         nacionalidade, curso) in alunos:
        nasc = nascimento.strftime("%d/%m/%Y") if nascimento else "-"
        print(f"{id_:<4} {nome:<26} {profissao or '-':<21} {nasc:<11} "
              f"{sexo or '-':<5} {peso if peso is not None else '-':>7} "
              f"{altura if altura is not None else '-':>6}  "
              f"{nacionalidade or '-':<14} {curso if curso is not None else '-':>5}")
    print(f"\nTotal: {len(alunos)} aluno(s).")


def exibir_menu():
    print("\n===== CADASTRO DE ALUNOS =====")
    print("1 - Cadastrar aluno   (Create)")
    print("2 - Listar alunos     (Read)")
    print("3 - Atualizar curso preferido (Update)")
    print("4 - Excluir aluno     (Delete)")
    print("0 - Sair")


# ======================================================================
# Operações do menu
# ======================================================================
def cadastrar_aluno(crud):
    print("\n--- Cadastrar aluno ---")
    nome = ler_texto("Nome: ", 30, obrigatorio=True)
    profissao = ler_texto("Profissão [Enter para pular]: ", 20)
    nascimento = ler_data("Nascimento (DD/MM/AAAA) [Enter para pular]: ")
    sexo = ler_sexo()
    peso = ler_decimal("Peso em kg [Enter para pular]: ", Decimal("999.99"))
    altura = ler_decimal("Altura em m [Enter para pular]: ", Decimal("9.99"))
    nacionalidade = ler_texto("Nacionalidade [Enter = Brasil]: ", 20) or "Brasil"
    curso = ler_inteiro("ID do curso preferido [Enter para pular]: ", opcional=True)

    novo_id = crud.criar(nome, profissao, nascimento, sexo, peso, altura,
                         nacionalidade, curso)
    print(f"Aluno cadastrado com sucesso! ID: {novo_id}")


def listar_alunos(crud):
    print("\n--- Listar alunos ---")
    print("1 - Todos | 2 - Buscar por ID | 3 - Buscar por nome")
    opcao = input("Escolha: ").strip()
    if opcao == "1":
        exibir_alunos(crud.ler())
    elif opcao == "2":
        exibir_alunos(crud.ler("id", ler_inteiro("ID do aluno: ")))
    elif opcao == "3":
        nome = ler_texto("Nome (ou parte dele): ", 30, obrigatorio=True)
        exibir_alunos(crud.ler("nome", nome))
    else:
        print("Opção inválida.")


def atualizar_curso_preferido(crud):
    print("\n--- Atualizar curso preferido ---")
    campo, valor = escolher_criterio()
    if campo is None:
        return

    encontrados = crud.buscar_exato(campo, valor)
    if not encontrados:
        print("Nenhum aluno encontrado com esse critério.")
        return
    exibir_alunos(encontrados)

    if len(encontrados) > 1:
        print(f"Atenção: {len(encontrados)} alunos têm esse nome e todos serão atualizados.")
        if not confirmar("Deseja continuar? (s/n): "):
            print("Operação cancelada.")
            return

    curso = ler_inteiro(
        "Novo curso preferido (idcurso) [Enter para deixar vazio]: ", opcional=True
    )
    crud.atualizar_curso_preferido(campo, valor, curso)
    print(f"{len(encontrados)} aluno(s) atualizado(s) com sucesso!")


def excluir_aluno(crud):
    print("\n--- Excluir aluno ---")
    campo, valor = escolher_criterio()
    if campo is None:
        return

    encontrados = crud.buscar_exato(campo, valor)
    if not encontrados:
        print("Nenhum aluno encontrado com esse critério.")
        return
    exibir_alunos(encontrados)

    if not confirmar(f"Excluir {len(encontrados)} aluno(s)? Esta ação não pode ser desfeita (s/n): "):
        print("Operação cancelada.")
        return

    crud.excluir(campo, valor)
    print(f"{len(encontrados)} aluno(s) excluído(s) com sucesso!")


def tratar_erro(erro):
    if erro.errno == errorcode.ER_NO_REFERENCED_ROW_2:
        print("Erro: o curso informado não existe. Use um idcurso válido da tabela cursos.")
    else:
        print(f"Erro no banco de dados: {erro}")


OPERACOES = {
    "1": cadastrar_aluno,
    "2": listar_alunos,
    "3": atualizar_curso_preferido,
    "4": excluir_aluno,
}


# ======================================================================
# Programa principal: a conexão é criada aqui
# ======================================================================
def main():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # coloque aqui a senha do seu MySQL, se houver
            database="cadastro",
        )
    except mysql.connector.Error as erro:
        print(f"Não foi possível conectar ao banco de dados: {erro}")
        return

    crud = AlunosCRUD(conexao)

    try:
        while True:
            exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("Encerrando o programa...")
                break

            operacao = OPERACOES.get(opcao)
            if operacao is None:
                print("Opção inválida.")
                continue

            try:
                operacao(crud)
            except mysql.connector.Error as erro:
                tratar_erro(erro)
    finally:
        crud.fechar()
        conexao.close()


if __name__ == "__main__":
    main()
