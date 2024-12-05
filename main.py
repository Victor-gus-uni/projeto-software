import tkinter # Interface gráfica
import sqlite3 # Banco de dados
import re # Verificar se email é valido
import webbrowser # Enviar usuário para um site no navegador
from PIL import Image, ImageTk # Manipulação de imagens no software
from tkinter import ttk # Usado para treeview e Combobox
from tkinter import messagebox # Exibir mensagens de erro e sucesso
from tkinter import filedialog # Selecionar imagens do computador
from tkinter import Menu # Criar menubar

caminho_logo = None
modo_favoritas = False

# Criação do banco de dados
def conecta_bd():
    conn = sqlite3.connect("ongs.db")
    cursor = conn.cursor()

    # Criando tabela usuarios
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    # Criando tabela tipo de ongs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tipo_ongs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        descricao TEXT NOT NULL
    )
    """)

    # Criando tabela estados
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estados (
        id integer PRIMARY KEY AUTOINCREMENT,
        codigo_estado char(2) NOT NULL UNIQUE,
        estado TEXT NOT NULL UNIQUE
    )
    """)

    # Criando tabela ongs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ongs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        logo TEXT DEFAULT 'logos/sem_logo.png',
        nome TEXT NOT NULL,
        endereco TEXT NOT NULL,
        cidade TEXT NOT NULL,
        telefone TEXT NOT NULL UNIQUE,
        id_tipo_ong INTEGER,
        id_estado INTEGER,
        FOREIGN KEY (id_tipo_ong) REFERENCES tipo_ongs(id),
        FOREIGN KEY (id_estado) REFERENCES estados(id)
    )
    """)

    # Criando tabela avaliacoes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_ong INTEGER NOT NULL,
        nota INTEGER CHECK(nota IN (0, 1)) NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
        FOREIGN KEY (id_ong) REFERENCES ongs(id)
    );
    """)

    # Criando previamente dados para tabela usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios = [
            ("exemplo", "exemplo@email.com", "exemplo123"),
            ("exemplo2", "exemplo2@email.com", "senha123"),
            ("exemplo3", "exemplo3@email.com", "senha456")
        ]
        cursor.executemany("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", usuarios)

    # Criando previamente dados para tabela tipo_ongs
    cursor.execute("SELECT COUNT(*) FROM tipo_ongs")
    if cursor.fetchone()[0] == 0:
        tipos_ongs = [
            ("Saúde",),
            ("Educação",),
            ("Meio Ambiente",),
            ("Direitos Humanos",),
            ("Cultura",),
            ("Alimento",),
            ("Vulnerabilidade Social",)
        ]
        cursor.executemany("INSERT INTO tipo_ongs (descricao) VALUES (?)", tipos_ongs)

    # Criando previamente dados para a tabela estados
    cursor.execute("SELECT COUNT(*) FROM estados")
    if cursor.fetchone()[0] == 0:
        estados = [
            ("AC", "Acre"),
            ("AL", "Alagoas"),
            ("AP", "Amapá"),
            ("AM", "Amazonas"),
            ("BA", "Bahia"),
            ("CE", "Ceará"),
            ("DF", "Distrito Federal"),
            ("ES", "Espírito Santo"),
            ("GO", "Goiás"),
            ("MA", "Maranhão"),
            ("MT", "Mato Grosso"),
            ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"),
            ("PA", "Pará"),
            ("PB", "Paraíba"),
            ("PR", "Paraná"),
            ("PE", "Pernambuco"),
            ("PI", "Piauí"),
            ("RJ", "Rio de Janeiro"),
            ("RN", "Rio Grande do Norte"),
            ("RS", "Rio Grande do Sul"),
            ("RO", "Rondônia"),
            ("RR", "Roraima"),
            ("SC", "Santa Catarina"),
            ("SP", "São Paulo"),
            ("SE", "Sergipe"),
            ("TO", "Tocantins"),
        ]
        cursor.executemany("INSERT INTO estados (codigo_estado, estado) VALUES (?, ?)", estados)

    # Criando previamente dados para tabela ongs
    cursor.execute("SELECT COUNT(*) FROM ongs")
    if cursor.fetchone()[0] == 0:
        ongs = [
            ("logos/amigosdobem.jpg", "Amigos do Bem", "R. 24 de Maio, 104 - República", "São Paulo", "(11) 93019 0107",
             2, 25),
            ("logos/mochileirosdecristo.jpg", "Mochileiros de Cristo", "R. Estevão Baião, 521 - Vila Congonhas",
             "São Paulo", "(11) 98121-4229", 2, 25),
            (
                "logos/saovicentedepaulo.jpeg", "Recanto São Vicente de Paulo",
                "Av. Jabaquara, 2180 - Bairro Mirandópolis",
                "São Paulo", "(11) 91364-9589", 2, 25),
            ("logos/ssvp.png", "Sociedade de São Vicente de Paulo", "Rua Manfredo, 8B - Morro Grande", "São Paulo",
             "(11) 96949-1381", 2, 25),
            ("logos/votutu.jpg", "Instituto Ações Sociais Vó Tutu", "Rua Virajuba, 1099, Brasilândia", "São Paulo",
             "(11) 93203-6116", 6, 25),
            ("logos/aafesp.png", "Associação de Anemia Falciforme do Estado de São Paulo - AAFESP",
             "Rua Boacica, 422 – Cidade Patriarca", "São Paulo", "(11) 99382-9176", 1, 25),
            ("logos/paopraquemtemfome.jpg", "Pão Pra Quem Tem Fome", "R. Santa Beatriz, 103 - Jardim Ibitirama",
             "São Paulo", "(11) 99291-0939", 6, 25),
            ("logos/redegeracaosolidaria.jpg", "Rede Geração Solidária", "R. Dr. Zuquim, 1959 - Água Fria", "São Paulo",
             "(11) 95131-7703", 2, 25),
            ("logos/cerzindo.png", "Projeto Cerzindo", "Rua Barra Funda, 1020", "São Paulo", "(11) 98532-2538", 7, 25),
            ("logos/CCA.png", "CCA São Paulo da Cruz", "Rua Cardeal Arcoverde, 950 - Jardim Paulista", "São Paulo",
             "(11) 93088-5766", 7, 25),
        ]
        cursor.executemany("""
            INSERT INTO ongs (logo, nome, endereco, cidade, telefone, id_tipo_ong, id_estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ongs)

    conn.commit()
    conn.close()


# Função cadastrar usuarios novos
def cadastrar_usuario():
    nome = nomeRegister_entry.get()
    email = emailRegister_entry.get()
    senha = senhaRegister_entry.get()
    confirmar_senha = senhaConfirmarRegister_entry.get()

    if not nome or not email or not senha or not confirmar_senha:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
        return

    if senha != confirmar_senha:
        messagebox.showerror("Erro", "Senhas não coincidem.")
        return

    # Garantir que o email seja valido
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        messagebox.showerror('Erro', 'e-mail inválido.')
        return

    try:
        conn = sqlite3.connect("ongs.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
        limpar_tela_bemvindo()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Email já cadastrado!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao registrar: {e}")


# Função usuario logar no aplicativo
def login_usuario():
    email = email_entry.get()
    senha = senha_entry.get()

    if not email or not senha:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return

    try:
        conn = sqlite3.connect("ongs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            global id_usuario
            id_usuario = usuario[0]
            mostrar_tela(tela_ongs)
            carregar_ongs()
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario[1]}!")
            limpar_tela_bemvindo()
        else:
            messagebox.showerror("Erro", "Email ou senha inválidos!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao fazer login: {e}")


# Mostrar as ONGs em tabela com o treeview
def carregar_ongs():
    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute(""" 
                SELECT o.id, o.logo, o.nome, o.endereco, o.cidade, e.estado, o.telefone, t.descricao 
                FROM ongs o 
                INNER JOIN estados e ON o.id_estado = e.id
                INNER JOIN tipo_ongs t ON o.id_tipo_ong = t.id;
            """)
            ongs = cursor.fetchall()

            # Atualizar os comboboxes de tipo de ONGs e estados
            cursor.execute("SELECT descricao FROM tipo_ongs")
            tipos = cursor.fetchall()
            tipo_combobox["values"] = [tipo[0] for tipo in tipos]

            cursor.execute("SELECT estado FROM estados")
            estados = cursor.fetchall()
            estado_combobox["values"] = [estado[0] for estado in estados]

    except sqlite3.OperationalError as e:
        messagebox.showerror("Erro", f"Erro ao carregar as ONGs: {e}")
        return

    # Atualizar a Treeview
    for item in treeview.get_children():
        treeview.delete(item)

    for ong in ongs:
        id_ong, caminho_logo, nome, endereco, cidade, estado, telefone, tipo = ong
        treeview.insert("", "end", values=(id_ong, nome, endereco, cidade, estado, telefone, tipo, caminho_logo))


# Mostrar as ONGs favoritas em tabela com o treeview
def carregar_ongs_favoritas():
    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.logo, o.nome, o.endereco, o.cidade, e.estado, o.telefone, t.descricao 
                    FROM ongs o 
                    INNER JOIN estados e ON o.id_estado = e.id
                    INNER JOIN tipo_ongs t ON o.id_tipo_ong = t.id
                    INNER JOIN avaliacoes a ON o.id = a.id_ong 
                    WHERE a.id_usuario = ? AND a.nota = 1;
            """, (id_usuario,))
            ongs_favoritas = cursor.fetchall()

    except sqlite3.OperationalError as e:
        messagebox.showerror("Erro", f"Erro ao carregar as ONGS favoritas: {e}")
        return

    for item in treeview.get_children():
        treeview.delete(item)

    for ong in ongs_favoritas:
        id_ong, caminho_logo, nome, endereco, cidade, estado, telefone, tipo = ong
        treeview.insert("", "end", values=(id_ong, nome, endereco, cidade, estado, telefone, tipo, caminho_logo))


def alternar_modo():
    global modo_favoritas

    # Exibir todas ONGs
    if modo_favoritas:
        carregar_ongs()
        favoritas_botao.config(text="Favoritas", command=alternar_modo)
        modo_favoritas = False
        limpar_tela_ongs()
    # Exibir ONGs favoritas
    else:
        carregar_ongs_favoritas()
        favoritas_botao.config(text="Voltar", command=alternar_modo)
        modo_favoritas = True
        limpar_tela_ongs()


# Pegar logo do computador
def chamar_logo():
    global caminho_logo
    caminho_logo = filedialog.askopenfilename(
        filetypes=[("Arquivos de imagem", "*.png *.jpg *.jpeg *.bmp *.gif")]
    )
    if not caminho_logo:
        caminho_logo = 'logos/sem_logo.png'  # Valor padrão se nenhuma imagem for escolhida
        messagebox.showinfo("Info", "Nenhuma imagem selecionada. Usando logo padrão.")
    else:
        try:
            img = Image.open(caminho_logo)
            img = img.resize((150, 150))  # Redimensionar a imagem para caber no espaço
            img_tk = ImageTk.PhotoImage(img)
            logo_label.config(image=img_tk)
            logo_label.image = img_tk
            return caminho_logo
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar a imagem: {e}")
            caminho_logo = 'logos/sem_logo.png'


def limpar_logo():
    global caminho_logo
    logo_label.config(image="", text="Logo")
    logo_label.image = None
    caminho_logo = None


# Adicionar ONG nova
def adicionar_ong():
    # Pegar os dados das entrys e comboboxes
    nome = nome_entry.get()
    endereco = endereco_entry.get()
    cidade = cidade_entry.get()
    estado = estado_combobox.get()
    telefone = telefone_entry.get()
    tipo = tipo_combobox.get()

    if not nome or not endereco or not cidade or not estado or not telefone or not tipo:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
        return

    # Verificar logo
    if caminho_logo:
        logo = caminho_logo
    else:
        logo = 'logos/sem_logo.png'

    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM estados WHERE estado = ?", (estado,))
            id_estado = cursor.fetchone()
            if not id_estado:
                messagebox.showerror("Erro", "Estado inválido. Selecione um estado válido.")
                return
            id_estado = id_estado[0]
            cursor.execute("SELECT id FROM tipo_ongs WHERE descricao = ?", (tipo,))
            id_tipo_ong = cursor.fetchone()
            if not id_tipo_ong:
                messagebox.showerror("Erro", "Tipo de ONG inválido.")
                return
            id_tipo_ong = id_tipo_ong[0]
            cursor.execute("""
                INSERT INTO ongs (logo, nome, endereco, cidade, id_estado, telefone, id_tipo_ong)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (logo, nome, endereco, cidade, id_estado, telefone, id_tipo_ong))
            conn.commit()
        carregar_ongs()
        limpar_tela_ongs()
        messagebox.showinfo("Sucesso", "ONG adicionada com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar ONG: {e}")


# Atualizar ONG
def atualizar_ong():
    item_selecionado = treeview.selection()
    if not item_selecionado:
        messagebox.showerror("Erro", "Selecione uma ONG para atualizar!")
        return

    item_values = treeview.item(item_selecionado)["values"]
    id_ong = item_values[0]

    nome = nome_entry.get()
    endereco = endereco_entry.get()
    cidade = cidade_entry.get()
    estado = estado_combobox.get()
    telefone = telefone_entry.get()
    tipo = tipo_combobox.get()

    if caminho_logo:
        logo = caminho_logo
    else:
        logo = 'logos/sem_logo.png'

    if not nome or not endereco or not cidade or not estado or not telefone or not tipo:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
        return

    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM estados WHERE estado = ?", (estado,))
            id_estado = cursor.fetchone()
            id_estado = id_estado[0] if id_estado else None
            cursor.execute("SELECT id FROM tipo_ongs WHERE descricao = ?", (tipo,))
            id_tipo_ong = cursor.fetchone()
            id_tipo_ong = id_tipo_ong[0] if id_tipo_ong else None
            cursor.execute("""
                UPDATE ongs 
                SET logo = ?, nome = ?, endereco = ?, cidade = ?, id_estado = ?, telefone = ?, id_tipo_ong = ?
                WHERE id = ?
            """, (logo, nome, endereco, cidade, id_estado, telefone, id_tipo_ong, id_ong))
            conn.commit()

        if modo_favoritas:
            carregar_ongs_favoritas()
        else:
            carregar_ongs()

        limpar_tela_ongs()
        messagebox.showinfo("Sucesso", "ONG atualizada com sucesso!")
    except sqlite3.OperationalError as e:
        messagebox.showerror("Erro", f"Erro ao atualizar ONG: {e}")


# Excluir ONG
def excluir_ong():
    global modo_favoritas
    item_selecionado = treeview.selection()
    if not item_selecionado:
        messagebox.showerror("Erro", "Selecione uma ONG para excluir!")
        return
    item_values = treeview.item(item_selecionado)["values"]
    id_ong = item_values[0]

    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            # Verificar se o ID da ONG existe antes de excluir
            cursor.execute("SELECT id FROM ongs WHERE id = ?", (id_ong,))
            if cursor.fetchone() is None:
                messagebox.showerror("Erro", "ONG não encontrada no banco de dados.")
                return
            cursor.execute("DELETE FROM ongs WHERE id = ?", (id_ong,))
            conn.commit()

        if modo_favoritas:
            carregar_ongs_favoritas()
        else:
            carregar_ongs()

        limpar_tela_ongs()
        messagebox.showinfo("Sucesso", "ONG excluída com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir ONG: {e}")


# Favoritar ONG
def avaliar_ong(id_ong, nota):
    global modo_favoritas
    try:
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            # Verificando se o usuario já avaliou a ONG
            cursor.execute("""
                SELECT id from avaliacoes WHERE id_usuario = ? AND id_ong = ?
            """, (id_usuario, id_ong))
            avaliacao_existente = cursor.fetchone()

            if avaliacao_existente:
                # Atualizar avaliação
                cursor.execute("""
                    UPDATE avaliacoes SET nota = ? WHERE id = ?
                """, (nota, avaliacao_existente[0]))
                messagebox.showinfo("Sucesso", "Avaliação atualizada")
            else:
                cursor.execute("""
                    INSERT INTO avaliacoes(id_usuario, id_ong, nota) VALUES (?, ?, ?)
                """, (id_usuario, id_ong, nota))
                messagebox.showinfo("Sucesso", "Avaliação registrada")
            conn.commit()

            if modo_favoritas and nota == 0:
                carregar_ongs_favoritas()
                limpar_tela_ongs()

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao registrar avaliação: {e}")


# Colocar dados da ONG nas entrys e comboboxes ao dar duplo clique na ONG na treeview
def doubleclick_treeview(event):
    # Obter o item selecionado na Treeview
    item_selecionado = treeview.selection()
    if item_selecionado:
        item_values = treeview.item(item_selecionado[0])["values"]

        # Preencher os campos com os valores da linha selecionada
        nome_entry.delete(0, tkinter.END)
        nome_entry.insert(0, item_values[1])  # Nome

        endereco_entry.delete(0, tkinter.END)
        endereco_entry.insert(0, item_values[2])  # Endereço

        cidade_entry.delete(0, tkinter.END)
        cidade_entry.insert(0, item_values[3])  # Cidade

        estado_combobox.set(item_values[4])  # Estado

        telefone_entry.delete(0, tkinter.END)
        telefone_entry.insert(0, item_values[5])  # Telefone

        tipo_combobox.set(item_values[6])  # Tipo

        global caminho_logo
        caminho_logo = item_values[7] if item_values[7] else 'logos/sem_logo.png'
        if caminho_logo and caminho_logo != "":  # Verifica se há uma imagem associada
            try:
                img = Image.open(caminho_logo)
                img = img.resize((150, 150))  # Redimensionar a imagem
                img_tk = ImageTk.PhotoImage(img)
                logo_label.config(image=img_tk)
                logo_label.image = img_tk
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar a logo: {e}")

        # Atualizar ID
        id_entry.configure(state='normal')  # Habilitar temporariamente
        id_entry.delete(0, tkinter.END)
        id_entry.insert(0, item_values[0])  # Inserir o ID
        id_entry.configure(state='readonly')  # Tornar readonly novamente


# Ordenar coluna em ordem crescente ou decrescente quando clicar em coluna
def ordenar_coluna(treeview, coluna, reverso):
    # Converter valores para números quando necessário
    def converter(valor):
        try:
            return int(valor)
        except ValueError:
            return valor

    # Obter os valores e converter
    dados = [(converter(treeview.set(item, coluna)), item) for item in treeview.get_children('')]

    # Ordenar os dados
    dados.sort(reverse=reverso)

    # Reorganizar os itens no Treeview
    for index, (_, item) in enumerate(dados):
        treeview.move(item, '', index)

    # Alternar a ordem para o próximo clique
    treeview.heading(coluna, command=lambda: ordenar_coluna(treeview, coluna, not reverso))


# Limpar entrys na tela inicial
def limpar_tela_bemvindo():
    # Limpar campos de login
    email_entry.delete(0, tkinter.END)
    senha_entry.delete(0, tkinter.END)

    # Limpar campos de cadastro
    nomeRegister_entry.delete(0, tkinter.END)
    emailRegister_entry.delete(0, tkinter.END)
    senhaRegister_entry.delete(0, tkinter.END)
    senhaConfirmarRegister_entry.delete(0, tkinter.END)


# Limpar entrys na tela de ONGs
def limpar_tela_ongs():
    # Limpar campos de entrada de texto
    id_entry.configure(state='normal')  # Habilitar o campo ID temporariamente para limpeza
    id_entry.delete(0, tkinter.END)
    id_entry.configure(state='readonly')  # Restaurar estado original

    nome_entry.delete(0, tkinter.END)
    endereco_entry.delete(0, tkinter.END)
    cidade_entry.delete(0, tkinter.END)
    estado_combobox.set("")
    telefone_entry.delete(0, tkinter.END)
    tipo_combobox.set("")

    limpar_logo()


# Criar nova janela para editar tipo_ong
def janela_tipo():
    def carregar_tipos():
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, descricao FROM tipo_ongs")
            tipos = cursor.fetchall()
            tipo_combobox["values"] = [tipo[1] for tipo in tipos]
            # Salva os IDs para referência
            global tipos_ids
            tipos_ids = {tipo[1]: tipo[0] for tipo in tipos}

    def adicionar_tipo():
        descricao = tipo_combobox.get().strip()
        if not descricao:
            messagebox.showerror("Erro", "O campo 'Descrição' não pode estar vazio.")
            return
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tipo_ongs (descricao) VALUES (?)", (descricao,))
            conn.commit()
        carregar_tipos()

        if modo_favoritas:
            carregar_ongs_favoritas()
        else:
            carregar_ongs()

        tipo_combobox.delete(0, tkinter.END)

    def atualizar_tipo():
        descricao = tipo_combobox.get().strip()
        tipo_selecionado = tipo_combobox.get()
        if not descricao:
            messagebox.showerror("Erro", "O campo 'Descrição' não pode estar vazio.")
            return
        if not tipo_selecionado or tipo_selecionado not in tipos_ids:
            messagebox.showerror("Erro", "Selecione um tipo válido para atualizar.")
            return
        id_tipo = tipos_ids[tipo_selecionado]
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tipo_ongs SET descricao = ? WHERE id = ?", (descricao, id_tipo))
            conn.commit()
        carregar_tipos()

        if modo_favoritas:
            carregar_ongs_favoritas()
        else:
            carregar_ongs()

        tipo_combobox.delete(0, tkinter.END)

    def excluir_tipo():
        tipo_selecionado = tipo_combobox.get()
        if not tipo_selecionado or tipo_selecionado not in tipos_ids:
            messagebox.showerror("Erro", "Selecione um tipo válido para excluir.")
            return
        id_tipo = tipos_ids[tipo_selecionado]
        with sqlite3.connect("ongs.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tipo_ongs WHERE id = ?", (id_tipo,))
            conn.commit()
        carregar_tipos()

        if modo_favoritas:
            carregar_ongs_favoritas()
        else:
            carregar_ongs()

        tipo_combobox.delete(0, tkinter.END)

    # Configuração da Janela
    root_tipo = tkinter.Toplevel()
    root_tipo.title("Gerenciar Tipos de ONGs")
    root_tipo.geometry("400x300")
    root_tipo.resizable(False, False)
    root_tipo.configure(bg="#ECF0F1", highlightbackground="#659db5", highlightcolor="#548396", highlightthickness=3)

    tipo_label = tkinter.Label(root_tipo, text="Tipo de ONG:", fg="#507e91", font=("Arial", 15))
    tipo_label.pack(pady=5)
    tipo_combobox = ttk.Combobox(root_tipo, width=30)
    tipo_combobox.pack(pady=5)

    botoes_frame = tkinter.Frame(root_tipo)
    botoes_frame.pack(pady=30)
    adicionar_tipo_botao = tkinter.Button(botoes_frame, activebackground="#507e91", activeforeground="#ECF0F1",
                                          fg="#507e91", text="Adicionar", font=("Arial", 18), command=adicionar_tipo)
    adicionar_tipo_botao.grid(row=0, column=0, padx=10)

    atualizar_tipo_botao = tkinter.Button(botoes_frame, activebackground="#507e91", activeforeground="#ECF0F1",
                                          fg="#507e91", text="Atualizar", font=("Arial", 18), command=atualizar_tipo)
    atualizar_tipo_botao.grid(row=0, column=1, padx=10)

    excluir_tipo_botao = tkinter.Button(botoes_frame, activebackground="#507e91", activeforeground="#ECF0F1",
                                        fg="#507e91", text="Excluir", font=("Arial", 18), command=excluir_tipo)
    excluir_tipo_botao.grid(row=0, column=2, padx=10)

    # Carregar dados ao abrir a janela
    carregar_tipos()


def Quit():
    root.destroy()


def deslogar():
    global tela_ativa, modo_favoritas
    if tela_ativa == tela_ongs:
        mostrar_tela(tela_bemvindo)
        limpar_tela_ongs()
        messagebox.showinfo("Logout", "Você foi deslogado com sucesso!")
        modo_favoritas = False
        favoritas_botao.config(text="Favoritas", command=alternar_modo)
    else:
        messagebox.showerror("Login", "Precisa logar primeiro.")


def abrir_site():
    url = "https://vinicius-cienci-space.wpkubio.com/ongs-aqui/?kubio-preview=saved&kubio-random=hJymFpAXB-97D4Absdnb"
    webbrowser.open(url)


def mostrar_tela(frame):
    global tela_ativa
    tela_ativa = frame
    frame.tkraise()  # Coloca o frame à frente dos outros


# Configuração da janela principal
root = tkinter.Tk()
root.title("ONGs Aqui")
root.geometry("1280x720")
root.resizable(False, False)

conecta_bd()

# Criação das telas
tela_bemvindo = tkinter.Frame(root, bg="#d2d7d9")
frame_login = tkinter.Frame(root)
frame_cadastro = tkinter.Frame(root)

tela_ongs = tkinter.Frame(root)
frame_tabela = tkinter.Frame(root)
frame_entrada_de_dados = tkinter.Frame(root)

# Colocando todas as telas na mesma posição (sobrepostas)
for frame in (tela_bemvindo, frame_login, frame_cadastro, tela_ongs, frame_tabela, frame_entrada_de_dados):
    frame.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame_login = tkinter.Frame(tela_bemvindo, bg="#ECF0F1", highlightbackground="#659db5", highlightcolor="#548396",
                            highlightthickness=3, width="600", height="600")
frame_cadastro = tkinter.Frame(tela_bemvindo, bg="#ECF0F1", highlightbackground="#659db5", highlightcolor="#548396",
                               highlightthickness=3, width="600", height="600")
frame_login.place(x=25, y=65)
frame_cadastro.place(x=640, y=65)

# Tela de Bem-vindo
bemvindo_label = tkinter.Label(tela_bemvindo, text="Bem-vindo à ONGS Aqui!", bg="#d2d7d9", fg="#507e91",
                               font=("Arial", 30))
bemvindo_label.place(x=420, y=5)

# Tela de Login
login_label = tkinter.Label(frame_login, text="Login", fg="#507e91", font=("Arial", 30))
login_label.place(x=225, y=125)

email_label = tkinter.Label(frame_login, text="Email", fg="#507e91", font=("Arial", 18))
email_label.place(x=15, y=190)
email_entry = tkinter.Entry(frame_login, fg="#507e91", font=("Arial", 18))
email_entry.place(x=100, y=190, width=400)

senha_label = tkinter.Label(frame_login, text="Senha", fg="#507e91", font=("Arial", 18))
senha_label.place(x=15, y=240)
senha_entry = tkinter.Entry(frame_login, show="*", fg="#507e91", font=("Arial", 18))
senha_entry.place(x=100, y=240, width=400)

confirmarLogin_botao = tkinter.Button(frame_login, text="Confirmar Login", font=("Arial", 18),
                                      activebackground="#507e91", activeforeground="#ECF0F1", fg="#507e91", width=20,
                                      command=login_usuario)
confirmarLogin_botao.place(x=140, y=300)

# Tela de Cadastro
register_label = tkinter.Label(frame_cadastro, text="Cadastro", fg="#507e91", font=("Arial", 30))
register_label.place(x=225, y=125)

nomeRegister_label = tkinter.Label(frame_cadastro, text="Nome", fg="#507e91", font=("Arial", 18))
nomeRegister_label.place(x=15, y=190)
nomeRegister_entry = tkinter.Entry(frame_cadastro, fg="#507e91", font=("Arial", 18))
nomeRegister_entry.place(x=100, y=190, width=400)

emailRegister_label = tkinter.Label(frame_cadastro, text="Email", fg="#507e91", font=("Arial", 18))
emailRegister_label.place(x=15, y=240)
emailRegister_entry = tkinter.Entry(frame_cadastro, fg="#507e91", font=("Arial", 18))
emailRegister_entry.place(x=100, y=240, width=400)

senhaRegister_label = tkinter.Label(frame_cadastro, text="Senha", fg="#507e91", font=("Arial", 18))
senhaRegister_label.place(x=15, y=290)
senhaRegister_entry = tkinter.Entry(frame_cadastro, show="*", fg="#507e91", font=("Arial", 18))
senhaRegister_entry.place(x=100, y=290, width=400)

senhaConfirmarRegister_label = tkinter.Label(frame_cadastro, fg="#507e91", text="Confirmar Senha", font=("Arial", 18))
senhaConfirmarRegister_label.place(x=15, y=340)
senhaConfirmarRegister_entry = tkinter.Entry(frame_cadastro, show="*", fg="#507e91", font=("Arial", 18))
senhaConfirmarRegister_entry.place(x=205, y=340, width=295)

confirmarRegister_botao = tkinter.Button(frame_cadastro, text="Cadastrar", font=("Arial", 18), fg="#507e91",
                                         activebackground="#507e91", activeforeground="#ECF0F1", width=15,
                                         command=cadastrar_usuario)
confirmarRegister_botao.place(x=175, y=400)

# Tela de Ongs com Treeview

frame_tabela = tkinter.Frame(tela_ongs, bg="#ECF0F1", highlightbackground="#659db5", highlightcolor="#548396",
                             highlightthickness=3, width="1000", height="300")
frame_entrada_de_dados = tkinter.Frame(tela_ongs, bg="#ECF0F1", highlightbackground="#659db5", highlightcolor="#548396",
                                       highlightthickness=3, width="1000", height="350")
frame_tabela.place(x=125, y=65)
frame_entrada_de_dados.place(x=125, y=355)

titulo_resultados = tkinter.Label(tela_ongs, text="ONGs", fg="#507e91", font=("Arial", 20))
titulo_resultados.place(x=600, y=25)

# Adicionando as colunas sem a coluna de logo
treeview = ttk.Treeview(frame_tabela,
                        columns=("Id", "Nome", "Endereço", "Cidade", "Estado", "Telefone", "Tipo", "Logo"),
                        show="headings")

# Configurando as colunas
treeview.heading("Id", text="ID")
treeview.heading("Nome", text="Nome")
treeview.heading("Endereço", text="Endereço")
treeview.heading("Cidade", text="Cidade")
treeview.heading("Estado", text="Estado")
treeview.heading("Telefone", text="Telefone")
treeview.heading("Tipo", text="Tipo")

# Ordenar as colunas
for coluna in treeview["columns"]:
    treeview.heading(coluna, text=coluna, command=lambda c=coluna: ordenar_coluna(treeview, c, False))

# Definindo a largura das colunas
treeview.column("Id", width=50, anchor="w")
treeview.column("Nome", width=150, anchor="w")
treeview.column("Endereço", width=200, anchor="w")
treeview.column("Cidade", width=100, anchor="w")
treeview.column("Estado", width=100, anchor="w")
treeview.column("Telefone", width=150, anchor="w")
treeview.column("Tipo", width=100, anchor="w")

# Configurar a coluna oculta (Logo)
treeview.column("Logo", width=0, stretch=tkinter.NO)  # Ocultar a coluna de logo

# Evento de duplo clique
treeview.bind("<Double-1>", doubleclick_treeview)

# Colocar a treeview na tela
treeview.place(x=80, y=30)

id_label = tkinter.Label(frame_entrada_de_dados, text="Codigo:", fg="#507e91", font=("Arial", 15))
id_label.place(x=80, y=15)
id_entry = tkinter.Entry(frame_entrada_de_dados, state='readonly', fg="#507e91", font=("Arial", 15), width="5")
id_entry.place(x=160, y=15)

nome_label = tkinter.Label(frame_entrada_de_dados, text="Nome:", fg="#507e91", font=("Arial", 15))
nome_label.place(x=91, y=45)
nome_entry = tkinter.Entry(frame_entrada_de_dados, fg="#507e91", font=("Arial", 15))
nome_entry.place(x=160, y=45)

endereco_label = tkinter.Label(frame_entrada_de_dados, text="Endereço:", fg="#507e91", font=("Arial", 15))
endereco_label.place(x=58, y=75)
endereco_entry = tkinter.Entry(frame_entrada_de_dados, fg="#507e91", font=("Arial", 15))
endereco_entry.place(x=160, y=75)

cidade_label = tkinter.Label(frame_entrada_de_dados, text="Cidade:", fg="#507e91", font=("Arial", 15))
cidade_label.place(x=80, y=105)
cidade_entry = tkinter.Entry(frame_entrada_de_dados, fg="#507e91", font=("Arial", 15))
cidade_entry.place(x=160, y=105)

estado_label = tkinter.Label(frame_entrada_de_dados, text="Estado:", fg="#507e91", font=("Arial", 15))
estado_label.place(x=80, y=135)
estado_combobox = ttk.Combobox(frame_entrada_de_dados, state="readonly", font=("Arial", 15))
estado_combobox.place(x=160, y=135)

telefone_label = tkinter.Label(frame_entrada_de_dados, text="Telefone:", fg="#507e91", font=("Arial", 15))
telefone_label.place(x=70, y=165)
telefone_entry = tkinter.Entry(frame_entrada_de_dados, fg="#507e91", font=("Arial", 15))
telefone_entry.place(x=160, y=165)

tipo_label = tkinter.Label(frame_entrada_de_dados, text="Tipo:", fg="#507e91", font=("Arial", 15))
tipo_label.place(x=104, y=195)
tipo_combobox = ttk.Combobox(frame_entrada_de_dados, state="readonly", font=("Arial", 15))
tipo_combobox.place(x=160, y=195)

logo_label = tkinter.Label(frame_entrada_de_dados, fg="#507e91", text="Logo", borderwidth=2, relief="solid")
logo_label.place(x=600, y=130)

carregar_logo_botao = tkinter.Button(frame_entrada_de_dados, text="Carregar Logo", activebackground="#507e91",
                                     activeforeground="#ECF0F1", fg="#507e91", font=("Arial", 15), command=chamar_logo)
carregar_logo_botao.place(x=600, y=285)

limpar_logo_botao = tkinter.Button(frame_entrada_de_dados, text="Retirar Logo", activebackground="#507e91",
                                   activeforeground="#ECF0F1", fg="#507e91", font=("Arial", 15), command=limpar_logo)
limpar_logo_botao.place(x=745, y=285)

favoritas_botao = tkinter.Button(frame_entrada_de_dados, text="Favoritas", font=("Arial", 18),
                                 activebackground="#507e91", activeforeground="#ECF0F1", fg="#507e91",
                                 command=alternar_modo)
favoritas_botao.place(x=765, y=5)

# Botões
adicionar_botao = tkinter.Button(frame_entrada_de_dados, text="Adicionar ONG", fg="#507e91", font=("Arial", 18),
                                 command=adicionar_ong)
adicionar_botao.place(x=25, y=250)

atualizar_botao = tkinter.Button(frame_entrada_de_dados, text="Atualizar ONG", activebackground="#507e91",
                                 activeforeground="#ECF0F1", fg="#507e91", font=("Arial", 18), command=atualizar_ong)
atualizar_botao.place(x=200, y=250)

excluir_botao = tkinter.Button(frame_entrada_de_dados, text="Excluir ONG", activebackground="#507e91",
                               activeforeground="#ECF0F1", fg="#507e91", font=("Arial", 18), command=excluir_ong)
excluir_botao.place(x=375, y=250)

# Avaliação
avaliacao_label = tkinter.Label(frame_entrada_de_dados, fg="#507e91", text="Avaliação:", font=("Arial", 18))
avaliacao_label.place(x=600, y=66)

# Botão para favoritar
avaliar_positivo_btn = tkinter.Button(frame_entrada_de_dados, text="Favoritar", bg="green", fg="white",
                                      activebackground="green", activeforeground="white",
                                      command=lambda: avaliar_ong(int(id_entry.get()), 1))
avaliar_positivo_btn.place(x=600, y=100)

# Botão para desfavoritar
avaliar_negativo_btn = tkinter.Button(frame_entrada_de_dados, text="Desfavoritar", bg="red", fg="white",
                                      activebackground="red", activeforeground="white",
                                      command=lambda: avaliar_ong(int(id_entry.get()), 0))
avaliar_negativo_btn.place(x=652, y=100)

# Adicionando menubar
menubar = Menu(tela_ongs, tearoff=0)
root.config(menu=menubar)
filemenu = Menu(menubar, tearoff=0)
filemenu2 = Menu(menubar, tearoff=0)

menubar.add_cascade(label="Sobre", menu=filemenu)
filemenu.add_command(label="Site", command=abrir_site)
menubar.add_cascade(label="Opções", menu=filemenu2)
filemenu2.add_command(label="Gerenciar Tipos ONGs", command=janela_tipo)
filemenu2.add_separator()
filemenu2.add_command(label="Logout", command=deslogar)
filemenu2.add_separator()
filemenu2.add_command(label="Sair", command=Quit)

# Começar com a tela de boas-vindas
mostrar_tela(tela_bemvindo)

root.mainloop()
