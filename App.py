#!/usr/bin/env python3
# 🎮 Desafio do Conhecimento 🌎💡 – versão leve com som compatível no Windows

import os
import json
import random
import tkinter as tk
from tkinter import messagebox
import google.generativeai as genai

# ---------- CONFIGURAÇÃO ---------- #
API_KEY = "AIzaSyBL7_A5r7m5m6Flk6euQB6eQiQAdr6A3kE"
genai.configure(api_key=API_KEY)
ARQUIVO_RANKING = "ranking.json"

# ---------- SOM (COM FALLBACK) ---------- #
def tocar_palmas():
    """Toca um som leve de palmas, ou imprime se não suportado."""
    try:
        import winsound
        for freq in [880, 960, 1020, 1100]:
            winsound.Beep(freq, 80)
    except Exception:
        print("👏 Palmas!")

def tocar_erro():
    """Som de erro curto."""
    try:
        import winsound
        winsound.Beep(220, 200)
    except Exception:
        print("❌ Erro!")

# ---------- RANKING ---------- #
def carregar_ranking():
    if os.path.exists(ARQUIVO_RANKING):
        with open(ARQUIVO_RANKING, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_ranking(ranking):
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=4, ensure_ascii=False)

# ---------- PERGUNTAS ---------- #
def gerar_pergunta_steam(nivel):
    try:
        prompt = (
            f"Crie uma pergunta interdisciplinar baseada na metodologia STEAM "
            f"para alunos do ensino fundamental, nível {nivel}. "
            "A pergunta deve integrar pelo menos dois dos temas: Português, Matemática, Ciências, Artes e Tecnologia. "
            "Responda apenas em JSON com as chaves: "
            "'pergunta', 'alternativas' (lista com 4 opções curtas), "
            "'correta' (texto da resposta certa), 'explicacao' (breve explicação de até 2 linhas)."
        )

        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(prompt)
        texto_raw = response.text

        import re
        m = re.search(r'\{.*\}', texto_raw, flags=re.DOTALL)
        if not m:
            print("⚠️ Resposta inválida:", texto_raw)
            return None

        data = json.loads(m.group(0))
        return {
            "texto": data.get("pergunta", "").strip(),
            "alternativas": [a.strip() for a in data.get("alternativas", [])[:4]],
            "correta": data.get("correta", "").strip(),
            "explicacao": data.get("explicacao", "").strip()
        }
    except Exception as e:
        print("❌ Erro ao gerar pergunta:", e)
        return None

# ---------- APP PRINCIPAL ---------- #
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Desafio do Conhecimento 🌎💡")
        self.root.geometry("880x620")
        self.root.config(bg="#f4f4f4")

        self.ranking = carregar_ranking()
        self.pontos = 0
        self.nome = ""
        self.nivel = "fácil"
        self.vidas = 3
        self.acertos_consecutivos = 0

        self.tela_inicio()

    def tela_inicio(self):
        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text="📘 Desafio do Conhecimento 🌎💡",
                 font=("Arial", 28, "bold"), bg="#f4f4f4").pack(pady=20)

        frame = tk.Frame(self.root, bg="#f4f4f4")
        frame.pack(pady=10)

        tk.Label(frame, text="Seu nome:", font=("Arial", 13), bg="#f4f4f4").grid(row=0, column=0, padx=5, pady=5)
        self.entry_nome = tk.Entry(frame, font=("Arial", 13), width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Nível de dificuldade:", font=("Arial", 13), bg="#f4f4f4").grid(row=1, column=0, padx=5)
        self.nivel_var = tk.StringVar(value="fácil")
        nivel_menu = tk.OptionMenu(frame, self.nivel_var, "fácil", "médio", "difícil")
        nivel_menu.config(font=("Arial", 12), width=22)
        nivel_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Iniciar Desafio 🚀", font=("Arial", 14, "bold"),
                  bg="#2e8b57", fg="white", command=self.iniciar).pack(pady=25)

        tk.Label(self.root, text="🏆 Ranking", font=("Arial", 15, "bold"),
                 bg="#f4f4f4").pack(pady=10)

        self.frame_rank = tk.Frame(self.root, bg="#f4f4f4")
        self.frame_rank.pack()
        self.atualizar_ranking()

    def atualizar_ranking(self):
        for w in self.frame_rank.winfo_children():
            w.destroy()
        if not self.ranking or not any(r["pontos"] > 0 for r in self.ranking):
            tk.Label(self.frame_rank, text="🎮 Jogue para aparecer no ranking!",
                     font=("Arial", 12, "italic"), bg="#f4f4f4", fg="gray").pack(pady=10)
            return
        for i, r in enumerate(sorted(self.ranking, key=lambda x: x["pontos"], reverse=True)):
            if r["pontos"] > 0:
                tk.Label(self.frame_rank, text=f"{i+1}. {r['nome']} — {r['pontos']} pts",
                         font=("Arial", 12), bg="#f4f4f4").pack(anchor="w")

    def iniciar(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite seu nome para começar.")
            return

        self.nome = nome
        self.nivel = self.nivel_var.get()
        self.pontos = 0
        self.vidas = 3
        self.acertos_consecutivos = 0
        self.nova_pergunta()

    def nova_pergunta(self):
        self.pergunta_atual = gerar_pergunta_steam(self.nivel)
        if not self.pergunta_atual:
            messagebox.showerror("Erro", "Falha ao gerar pergunta.")
            self.tela_inicio()
            return
        self.mostrar_pergunta()

    def mostrar_pergunta(self):
        for w in self.root.winfo_children():
            w.destroy()

        p = self.pergunta_atual
        header = tk.Frame(self.root, bg="#e9f5ef")
        header.pack(fill="x", pady=5)

        lbl_info = tk.Label(header,
                            text=f"{self.nome}  |  Pontos: {self.pontos}",
                            font=("Arial", 13, "bold"),
                            bg="#e9f5ef")
        lbl_info.pack(side="left", padx=20)

        lbl_vidas = tk.Label(header,
                             text=" ".join(["❤️"] * self.vidas),
                             font=("Arial", 18),
                             bg="#e9f5ef",
                             fg="red")
        lbl_vidas.pack(side="right", padx=20)

        tk.Label(self.root, text=p["texto"], wraplength=820,
                 font=("Arial", 16, "bold"), bg="#f4f4f4",
                 justify="center").pack(pady=25)

        frame = tk.Frame(self.root, bg="#f4f4f4")
        frame.pack(pady=10)

        for alt in p["alternativas"]:
            btn = tk.Button(frame, text=alt, font=("Arial", 13),
                            bg="#e8f5e9", fg="black",
                            wraplength=780, width=70, height=2,
                            relief="ridge", command=lambda a=alt: self.verificar(a))
            btn.pack(pady=6)

    def verificar(self, resposta):
        correta = self.pergunta_atual["correta"]
        if resposta.lower() == correta.lower():
            self.pontos += 10
            self.acertos_consecutivos += 1
            tocar_palmas()
            if self.acertos_consecutivos % 3 == 0 and self.vidas < 5:
                self.vidas += 1
                messagebox.showinfo("Bônus!", "🎉 Você ganhou um coração extra!")
            else:
                messagebox.showinfo("Correto!", f"✅ {self.pergunta_atual['explicacao']}")
        else:
            self.vidas -= 1
            self.acertos_consecutivos = 0
            tocar_erro()
            if self.vidas <= 0:
                self.game_over()
                return
            messagebox.showwarning("Errado!", f"❌ Resposta certa: {correta}\n\n{self.pergunta_atual['explicacao']}")
        self.nova_pergunta()

    def game_over(self):
        self.ranking.append({"nome": self.nome, "pontos": self.pontos})
        self.ranking = sorted(self.ranking, key=lambda x: x["pontos"], reverse=True)[:10]
        salvar_ranking(self.ranking)

        for w in self.root.winfo_children():
            w.destroy()

        tk.Label(self.root, text=f"🎮 Game Over, {self.nome}!",
                 font=("Arial", 22, "bold"), bg="#f4f4f4").pack(pady=25)
        tk.Label(self.root, text=f"Sua pontuação: {self.pontos}",
                 font=("Arial", 16), bg="#f4f4f4").pack(pady=10)

        tk.Button(self.root, text="Jogar Novamente 🔁", font=("Arial", 14, "bold"),
                  bg="#2e8b57", fg="white", command=self.tela_inicio).pack(pady=10)
        tk.Button(self.root, text="Sair", font=("Arial", 12),
                  command=self.root.destroy).pack(pady=5)

# ---------- EXECUÇÃO ---------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
