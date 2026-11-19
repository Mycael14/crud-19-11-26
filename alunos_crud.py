import mysql.connector


class AlunosCRUD:
    """Operações de CRUD da tabela `alunos`.

    A conexão é criada no arquivo principal (main.py) e recebida
    aqui já pronta, pelo construtor.
    """

    COLUNAS = "id, nome, profissao, nascimento, sexo, peso, altura, nacionalidade, curso_preferido"
    CRITERIOS_VALIDOS = ("id", "nome")

    def __init__(self, conexao):
        self.conexao = conexao
        self.cursor = conexao.cursor()

    def fechar(self):
        """Fecha apenas o cursor. A conexão é fechada no arquivo principal."""
        self.cursor.close()

    def _validar_criterio(self, campo):
        if campo not in self.CRITERIOS_VALIDOS:
            raise ValueError("Critério inválido: use 'id' ou 'nome'.")

    def _executar_e_confirmar(self, comando, valores):
        """Executa um comando que altera o banco, com commit/rollback."""
        try:
            self.cursor.execute(comando, valores)
            self.conexao.commit()
        except mysql.connector.Error:
            self.conexao.rollback()
            raise

    # ---------------- CREATE ----------------
    def criar(self, nome, profissao, nascimento, sexo, peso, altura,
              nacionalidade, curso_preferido):
        comando = (
            "INSERT INTO alunos "
            "(nome, profissao, nascimento, sexo, peso, altura, nacionalidade, curso_preferido) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        valores = (nome, profissao, nascimento, sexo, peso, altura,
                   nacionalidade, curso_preferido)
        self._executar_e_confirmar(comando, valores)
        return self.cursor.lastrowid

    # ---------------- READ ----------------
    def ler(self, campo=None, valor=None):
        """Sem argumentos: lista todos os alunos.
        campo='id': busca exata pelo ID.
        campo='nome': busca parcial (LIKE) pelo nome.
        """
        if campo is None:
            self.cursor.execute(f"SELECT {self.COLUNAS} FROM alunos ORDER BY id")
        elif campo == "id":
            self.cursor.execute(
                f"SELECT {self.COLUNAS} FROM alunos WHERE id = %s", (valor,)
            )
        elif campo == "nome":
            self.cursor.execute(
                f"SELECT {self.COLUNAS} FROM alunos WHERE nome LIKE %s ORDER BY id",
                (f"%{valor}%",),
            )
        else:
            self._validar_criterio(campo)
        return self.cursor.fetchall()

    def buscar_exato(self, campo, valor):
        """Busca exata por ID ou Nome. Usada para conferir quem será
        afetado antes de um UPDATE ou DELETE."""
        self._validar_criterio(campo)
        # `campo` passou pela lista de critérios válidos, então é seguro no SQL.
        self.cursor.execute(
            f"SELECT {self.COLUNAS} FROM alunos WHERE {campo} = %s ORDER BY id",
            (valor,),
        )
        return self.cursor.fetchall()

    # ---------------- UPDATE ----------------
    def atualizar_curso_preferido(self, campo, valor, curso_preferido):
        """Atualiza a coluna curso_preferido (FK para cursos.idcurso)
        usando o ID ou o Nome do aluno como critério.
        Passe None em curso_preferido para deixar o campo vazio (NULL)."""
        self._validar_criterio(campo)
        comando = f"UPDATE alunos SET curso_preferido = %s WHERE {campo} = %s"
        self._executar_e_confirmar(comando, (curso_preferido, valor))
        return self.cursor.rowcount

    # ---------------- DELETE ----------------
    def excluir(self, campo, valor):
        """Exclui aluno(s) usando o ID ou o Nome como critério."""
        self._validar_criterio(campo)
        comando = f"DELETE FROM alunos WHERE {campo} = %s"
        self._executar_e_confirmar(comando, (valor,))
        return self.cursor.rowcount
