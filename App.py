import tkinter as tk
from tkinter import messagebox, scrolledtext
import google.generativeai as genai
import json
import threading
import os 

# ============ CONFIGURAÇÃO DO GEMINI ============
# ATENÇÃO: A chave de API fornecida é inválida. Substitua "SUA_CHAVE_AQUI" pela sua chave válida.
genai.configure(api_key="AIzaSyBL7_A5r7m5m6Flk6euQB6eQiQAdr6A3kE")

try:
    # Corrigido para gemini-2.5-flash, o modelo atualmente recomendado.
    gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")  
except Exception as e:
    gemini_model = None
    print(f"⚠️ Erro ao inicializar o modelo Gemini. Verifique a chave de API: {e}")

# ============ CONFIGURAÇÃO DO RANKING ============
RANKING_FILE = "ranking.json"

def carregar_ranking():
    """Carrega o ranking do arquivo JSON."""
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_ranking(ranking_data):
    """Salva o ranking no arquivo JSON."""
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranking_data, f, ensure_ascii=False, indent=4)

# ============ CLASSE PRINCIPAL ============
class JogoQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Desafio do Conhecimento 🎓")
        self.root.geometry("800x600")
        self.root.configure(bg="#E9F7EF") # Cor de fundo padrão

        self.nome_jogador = ""
        self.materia = None
        self.dificuldade = "Fácil" 
        self.pontuacao = 0
        self.vidas = 3
        self.acertos_consecutivos = 0 
        self.pergunta_atual = None
        self.gerando = False

        self.criar_tela_splash() # Começa na tela de introdução

    # ============ TELA DE SPLASH (INTRODUÇÃO) ============
    def criar_tela_splash(self):
        self.limpar_tela()
        # Define um fundo branco para a introdução, como na imagem
        self.root.configure(bg="white") 
        
        # Frame principal para centralizar o conteúdo
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(expand=True)

        # === Parte Superior: Informações da Universidade (sem logo) ===
        top_frame = tk.Frame(main_frame, bg="white")
        top_frame.pack(pady=(20, 10))

        # Texto da Universidade (agora alinhado diretamente na top_frame)
        tk.Label(top_frame, text="UNIVERSIDADE ESTADUAL DO NORTE",
                 font=("Arial", 14, "bold"), bg="white", fg="black", anchor="center").pack(fill="x", padx=20)
        tk.Label(top_frame, text="DO PARANÁ",
                 font=("Arial", 14, "bold"), bg="white", fg="black", anchor="center").pack(fill="x", padx=20)
        tk.Label(top_frame, text="Campus Cornélio Procópio",
                 font=("Arial", 12, "bold"), bg="white", fg="black", anchor="center").pack(fill="x", padx=20)
        
        # Linha separadora
        tk.Frame(main_frame, bg="#3366CC", height=2).pack(fill="x", padx=100, pady=5) # Azul como na imagem
        
        tk.Label(main_frame, text="PROGRAMA DE PÓS-GRADUAÇÃO EM ENSINO",
                 font=("Arial", 12), bg="white", fg="black").pack(pady=(5, 0))
        tk.Label(main_frame, text="MESTRADO PROFISSIONAL EM ENSINO",
                 font=("Arial", 12, "bold"), bg="white", fg="black").pack(pady=(0, 20))
        
        # === Nomes dos Desenvolvedores ===
        nomes = [
            "DANIELI GUEDES", "JULIANA TONHATO", "KARINA SANTANA,", 
            "LUANA FERREIRA", "LUÍS", "MARIA EDUARDA" , "MARCEL DANCINI" 
        ]
        
        for nome in nomes:
            tk.Label(main_frame, text=nome, font=("Arial", 12), bg="white", fg="black").pack(pady=0) 

        # === Títulos do Projeto ===
        tk.Label(main_frame, text="RELATÓRIO CRÍTICO/MEMORIAIS",
                 font=("Arial", 14, "bold"), bg="white", fg="#4CAF50").pack(pady=(40, 5)) 
        
        title_text = "GAMIFICAÇÃO E FEEDBACK ADAPTATIVO NA REVISÃO: UMA SOLUÇÃO STEAM PARA O FORTALECIMENTO DA BASE ESSENCIAL DO 7º ANO."
        tk.Label(main_frame, text=title_text,
                 font=("Arial", 14, "bold"), bg="white", fg="#4CAF50", wraplength=600, justify=tk.CENTER).pack(pady=(0, 40))
        
        # Botão para Iniciar
        tk.Button(main_frame, text="Clique aqui para iniciar", font=("Arial", 18, "bold"),
                  bg="#FFD700", fg="#1B5E20", activebackground="#FFEB3B", 
                  command=self.criar_tela_configuracao).pack(pady=20, ipadx=20, ipady=10)


    # ============ TELA DE CONFIGURAÇÃO (ANTIGA TELA INICIAL) ============
    def criar_tela_configuracao(self):
        self.limpar_tela()
        # Retorna a cor de fundo para a cor padrão do jogo
        self.root.configure(bg="#E9F7EF") 
        
        self.pontuacao = 0
        self.vidas = 3
        self.gerando = False
        self.acertos_consecutivos = 0 
        
        # Define o nível de escolaridade para o prompt do Gemini (mantido para contexto)
        DIFICULDADE_PROMPT = {
            "Fácil": "alunos do 7º ano",
            "Médio": "alunos do Ensino Médio",
            "Difícil": "nível universitário"
        }
        
        tk.Label(self.root, text="Desafio do Conhecimento 🎓",
                 font=("Arial", 26, "bold"), bg="#E9F7EF", fg="#1B5E20").pack(pady=30)

        # Entrada de Nome
        tk.Label(self.root, text="Digite seu nome:", bg="#E9F7EF", font=("Arial", 12)).pack()
        self.nome_entry = tk.Entry(self.root, font=("Arial", 12), width=30)
        self.nome_entry.pack(pady=5)
        self.nome_entry.insert(0, self.nome_jogador)

        # Escolha da Matéria
        tk.Label(self.root, text="Escolha a matéria:", bg="#E9F7EF", font=("Arial", 12)).pack(pady=10)
        self.materia_var = tk.StringVar(value=self.materia if self.materia else "Português")
        
        # MATÉRIAS ATUALIZADAS: Somente Português, Matemática e Geografia
        materias = ["Português", "Matemática", "Geografia"]
        
        for m in materias:
            tk.Radiobutton(self.root, text=m, variable=self.materia_var, value=m,
                           bg="#E9F7EF", font=("Arial", 11)).pack(anchor="w", padx=300)

        # Escolha da Dificuldade
        tk.Label(self.root, text="Escolha a dificuldade:", bg="#E9F7EF", font=("Arial", 12)).pack(pady=10)
        self.dificuldade_var = tk.StringVar(value=self.dificuldade)
        dificuldades = ["Fácil", "Médio", "Difícil"]
        
        # Frame para os botões de dificuldade ficarem lado a lado
        diff_frame = tk.Frame(self.root, bg="#E9F7EF")
        diff_frame.pack(pady=5)
        
        for d in dificuldades:
            tk.Radiobutton(diff_frame, text=d, variable=self.dificuldade_var, value=d,
                           bg="#E9F7EF", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)

        # Botões de Ação
        tk.Button(self.root, text="Iniciar Jogo", font=("Arial", 14, "bold"),
                  bg="#1B5E20", fg="white", command=self.iniciar).pack(pady=20)
        
        tk.Button(self.root, text="Ver Ranking", font=("Arial", 12),
                  bg="#006064", fg="white", command=self.exibir_ranking).pack(pady=10)


    # ============ INICIAR ============
    def iniciar(self):
        nome = self.nome_entry.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Digite seu nome para começar.")
            return
        
        if gemini_model is None:
            messagebox.showerror("Erro de API", 
                                 "O modelo Gemini não pôde ser inicializado.\n"
                                 "Por favor, verifique se sua chave de API está configurada corretamente no código.")
            return
            
        self.nome_jogador = nome
        self.materia = self.materia_var.get()
        self.dificuldade = self.dificuldade_var.get() # Salva a dificuldade escolhida
        self.carregar_proxima_pergunta("Gerando primeira pergunta...")

    # ============ TELA DE CARREGAMENTO ============
    def carregar_proxima_pergunta(self, texto="Carregando próxima pergunta..."):
        if self.gerando:
            return
        self.gerando = True
        self.limpar_tela()
        self.loading_label = tk.Label(self.root, text=texto, bg="#E9F7EF",
                                      font=("Arial", 16, "italic"), fg="#1B5E20")
        self.loading_label.pack(pady=250)
        self.animar_pontinhos(0)
        threading.Thread(target=self.gerar_pergunta_gemini).start()

    # ============ ANIMAÇÃO DE PONTINHOS ============
    def animar_pontinhos(self, count):
        if not self.gerando:
            return
        pontos = "." * (count % 4)
        self.loading_label.config(text=f"Carregando próxima pergunta{pontos}")
        self.root.after(400, lambda: self.animar_pontinhos(count + 1))

    # ============ GERAR PERGUNTA COM GEMINI ============
    def gerar_pergunta_gemini(self):
        # Mapeamento do nível de dificuldade para o prompt
        nivel_escolaridade = {
            "Fácil": "alunos do 7º ano",
            "Médio": "alunos do Ensino Médio",
            "Difícil": "nível universitário"
        }.get(self.dificuldade, "alunos do 7º ano")
        
        try:
            prompt = (
                f"Crie uma pergunta de múltipla escolha para {nivel_escolaridade} "
                f"sobre o tema '{self.materia}'. "
                "A resposta deve ser APENAS um JSON no formato: "
                '{"pergunta":"...","alternativas":{"A":"...","B":"...","C":"...","D":"..."},"correta":"A"} '
                "sem explicações, comentários ou texto adicional."
            )

            resposta = gemini_model.generate_content(prompt)
            texto = resposta.text.strip()

            if "```" in texto:
                texto = texto.replace("```json", "").replace("```", "").strip()

            dados = json.loads(texto)
            self.pergunta_atual = dados
            self.root.after(0, self.exibir_pergunta)

        except Exception as e:
            print("❌ Erro ao gerar pergunta:", e)
            self.gerando = False
            messagebox.showerror("Erro de Conexão/API", 
                                 "Não foi possível gerar uma pergunta.\n"
                                 "Verifique sua conexão com a internet ou se a chave de API está correta.")
            self.root.after(0, self.criar_tela_configuracao) # Volta para a tela de configuração em caso de erro

    # ============ EXIBIR PERGUNTA ============
    def exibir_pergunta(self):
        self.gerando = False
        self.limpar_tela()
        self.root.configure(bg="#E9F7EF") # Garante a cor de fundo correta para o jogo

        frame = tk.Frame(self.root, bg="#E9F7EF")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Exibe o número de acertos consecutivos
        info_text = f"Jogador: {self.nome_jogador} | Pontos: {self.pontuacao} | Dificuldade: {self.dificuldade}"
        tk.Label(frame, text=info_text,
                 bg="#E9F7EF", font=("Arial", 12, "italic")).pack(anchor="ne", pady=5)
        
        vidas_text = f"Vidas: {'❤️'*self.vidas} | Acertos Seguidos: {self.acertos_consecutivos}/3"
        tk.Label(frame, text=vidas_text, bg="#E9F7EF",
                 font=("Arial", 14, "bold")).pack(anchor="ne", pady=5)

        pergunta = self.pergunta_atual["pergunta"]
        alternativas = self.pergunta_atual["alternativas"]

        pergunta_box = scrolledtext.ScrolledText(frame, wrap="word", height=4,
                                                 width=80, font=("Arial", 13))
        pergunta_box.insert(tk.END, pergunta)
        pergunta_box.configure(state="disabled", bg="#F9FFF9")
        pergunta_box.pack(pady=10)

        self.resposta_var = tk.StringVar()
        for letra, texto in alternativas.items():
            tk.Radiobutton(frame, text=f"{letra}) {texto}",
                           variable=self.resposta_var, value=letra,
                           bg="#E9F7EF", font=("Arial", 12),
                           anchor="w", justify="left", wraplength=700).pack(fill="x", padx=40, pady=4)

        tk.Button(frame, text="Responder", bg="#1B5E20", fg="white",
                  font=("Arial", 13, "bold"), command=self.verificar_resposta).pack(pady=25)

    # ============ VERIFICAR RESPOSTA ============
    def verificar_resposta(self):
        resposta = self.resposta_var.get()
        if not resposta:
            messagebox.showinfo("Atenção", "Selecione uma alternativa.")
            return

        correta = self.pergunta_atual["correta"]
        if resposta.upper() == correta.upper():
            self.pontuacao += 10
            self.acertos_consecutivos += 1 # Aumenta acertos seguidos
            
            # NOVO: Verifica vida extra
            if self.acertos_consecutivos >= 3:
                self.vidas += 1
                self.acertos_consecutivos = 0 # Reseta
                messagebox.showinfo("⭐ BÔNUS! ⭐", "Três acertos seguidos! Você ganhou uma vida extra!")
            else:
                 messagebox.showinfo("🎉 Correto!", "Você acertou! +10 pontos")
                 
        else:
            self.vidas -= 1
            self.acertos_consecutivos = 0 # Reseta a contagem
            
            if self.vidas <= 0:
                self.game_over()
                return
            messagebox.showerror("❌ Errou!", f"A resposta certa era: {correta}\nVocê perdeu uma vida!")

        self.carregar_proxima_pergunta()

    # ============ GAME OVER ============
    def game_over(self):
        self.gerando = False
        
        # Adiciona a pontuação ao ranking
        novo_registro = {
            "nome": self.nome_jogador,
            "materia": self.materia,
            "dificuldade": self.dificuldade, 
            "pontuacao": self.pontuacao
        }
        ranking = carregar_ranking()
        ranking.append(novo_registro)
        salvar_ranking(ranking)
        
        self.limpar_tela()
        self.root.configure(bg="#F8D7DA") # Garante a cor de fundo correta
        frame = tk.Frame(self.root, bg="#F8D7DA")
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="💀 GAME OVER 💀", bg="#F8D7DA",
                 font=("Arial", 28, "bold"), fg="red").pack(pady=40)
        tk.Label(frame, text=f"{self.nome_jogador}, sua pontuação final foi: {self.pontuacao} ({self.dificuldade})",
                 bg="#F8D7DA", font=("Arial", 15)).pack(pady=10)
        
        # Botões de Ação
        tk.Button(frame, text="Jogar Novamente", bg="#1B5E20", fg="white",
                  font=("Arial", 14, "bold"), command=self.criar_tela_configuracao).pack(pady=10)
        tk.Button(frame, text="Ver Ranking", bg="#006064", fg="white",
                  font=("Arial", 14, "bold"), command=self.exibir_ranking).pack(pady=10)
        tk.Button(frame, text="Sair", bg="#8B0000", fg="white",
                  font=("Arial", 12, "bold"), command=self.root.destroy).pack(pady=5)
        
    # ============ EXIBIR RANKING ============
    def exibir_ranking(self):
        self.limpar_tela()
        self.root.configure(bg="#E9F7EF") # Garante cor de fundo correta
        ranking = carregar_ranking()
        
        # 1. Classificar o ranking pela pontuação (do maior para o menor)
        ranking_ordenado = sorted(ranking, key=lambda x: x['pontuacao'], reverse=True)
        
        tk.Label(self.root, text="🏆 Ranking dos Melhores 🏆",
                 font=("Arial", 24, "bold"), bg="#E9F7EF", fg="#006064").pack(pady=20)
        
        # Frame para a tabela do ranking
        ranking_frame = tk.Frame(self.root, bg="#FFFFFF", padx=10, pady=10, borderwidth=2, relief="groove")
        ranking_frame.pack(padx=50, pady=10, fill="x")
        
        # Cabeçalho: adicionada a coluna de Dificuldade
        colunas = ["Pos.", "Nome", "Matéria", "Dificuldade", "Pontos"]
        larguras = [5, 18, 12, 10, 8]
        
        for i, (coluna, largura) in enumerate(zip(colunas, larguras)):
            tk.Label(ranking_frame, text=coluna, font=("Arial", 12, "bold"), 
                     bg="#B2DFDB", fg="#004D40", width=largura, 
                     anchor="w" if i > 0 else "center", padx=5).grid(row=0, column=i, sticky="ew")

        # Dados do Ranking (Top 10)
        if not ranking_ordenado:
            tk.Label(ranking_frame, text="Nenhum registro de pontuação ainda.", 
                     font=("Arial", 12, "italic"), bg="#FFFFFF", pady=10).grid(row=1, column=0, columnspan=5, sticky="ew")
        else:
            for i, record in enumerate(ranking_ordenado[:10]):
                bg_color = "#E0F2F1" if i % 2 == 0 else "#FFFFFF"
                
                posicao = i + 1
                nome = record.get("nome", "Desconhecido")
                materia = record.get("materia", "N/A")
                dificuldade = record.get("dificuldade", "N/A") 
                pontuacao = record.get("pontuacao", 0)

                # Posição
                tk.Label(ranking_frame, text=f"#{posicao}", font=("Arial", 11), bg=bg_color, fg="#000000", 
                         width=larguras[0], anchor="center", padx=5).grid(row=i+1, column=0, sticky="ew")
                # Nome
                tk.Label(ranking_frame, text=nome, font=("Arial", 11), bg=bg_color, fg="#000000", 
                         width=larguras[1], anchor="w", padx=5).grid(row=i+1, column=1, sticky="ew")
                # Matéria
                tk.Label(ranking_frame, text=materia, font=("Arial", 11), bg=bg_color, fg="#000000", 
                         width=larguras[2], anchor="w", padx=5).grid(row=i+1, column=2, sticky="ew")
                # Dificuldade
                tk.Label(ranking_frame, text=dificuldade, font=("Arial", 11), bg=bg_color, fg="#000000", 
                         width=larguras[3], anchor="w", padx=5).grid(row=i+1, column=3, sticky="ew")
                # Pontos
                tk.Label(ranking_frame, text=str(pontuacao), font=("Arial", 11, "bold"), bg=bg_color, fg="#000000", 
                         width=larguras[4], anchor="w", padx=5).grid(row=i+1, column=4, sticky="ew")
                         
        # Botão Voltar (solicitado)
        tk.Button(self.root, text="Voltar ao Menu Principal", font=("Arial", 12, "bold"),
                  bg="#1B5E20", fg="white", command=self.criar_tela_configuracao).pack(pady=30)
        
    # ============ LIMPAR ============
    def limpar_tela(self):
        for w in self.root.winfo_children():
            w.destroy()


# ============ EXECUTAR ============
if __name__ == "__main__":
    root = tk.Tk()
    app = JogoQuiz(root)
    root.mainloop()
