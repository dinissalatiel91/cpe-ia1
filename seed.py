"""
seed.py
-------
Script para criar/actualizar:
- Admin (para gerir Q/A sem mexer no código)
- Alguns Q/A iniciais (CPE)

Executa:
  python seed.py

Depois entra com:
  Email: admin@uni.test
  Password: admin123
"""

from werkzeug.security import generate_password_hash
from app import create_app
from models import db, User, QAItem

app = create_app()

SEED_QA = [
    (
        "O que é comunicação pessoal e empresarial?",
        "É o conjunto de práticas e técnicas para comunicar de forma eficaz em contextos individuais (pessoal) e organizacionais (empresarial), garantindo clareza, objectividade, ética e adequação ao público."
    ),
    (
        "Quais são os elementos do processo de comunicação?",
        "Emissor, mensagem, canal, receptor, código, contexto e feedback. Podem existir ruídos que distorcem a mensagem."
    ),
    (
        "O que são barreiras da comunicação?",
        "Fatores que dificultam a compreensão da mensagem: ruído, linguagem inadequada, falta de atenção, preconceitos, emoções, excesso de informação e problemas no canal."
    ),
    (
        "Como escrever um email formal?",
        "Assunto claro, saudação adequada, corpo objectivo (um tema por email), linguagem profissional, pedido explícito, despedida e assinatura."
    ),
    (
        "O que é comunicação?",
        "Comunicação é o acto de transmitir informações, ideias ou sentimentos entre indivíduos ou grupos, permitindo a interacção por meio da linguagem."
    ),
    (
        "De onde deriva a palavra “comunicação”?",
        "Deriva do latim communicatio, que significa partilhar, trocar ideias, tornar comum."
    ),
    (
        "Qual é o principal objectivo da comunicação?",
        "Transmitir uma determinada informação e permitir a interacção entre indivíduos ou grupos."
    ),
    (
        "Cite três objectivos da comunicação.",
        "Compartilhar informações, interagir com os outros e persuadir o receptor."
    ),
    (
        "Quem é o emissor no processo comunicativo?",
        "É o agente que emite ou transmite a mensagem para o receptor."
    ),
    (
        "Quem é o receptor?",
        "É aquele que recebe a mensagem e a descodifica."
    ),
    (
        "O que é a mensagem?",
        "É o conjunto de enunciados que formam a informação transmitida."
    ),
    (
        "O que é o canal de comunicação?",
        "É o meio físico pelo qual a mensagem é transmitida, como voz, telefone, rádio, internet, carta, entre outros."
    ),
    (
        "O que se entende por código na comunicação?",
        "É o conjunto de sinais usados para codificar e descodificar a mensagem, como a língua, gestos e expressões faciais."
    ),
    (
        "O que é o contexto da comunicação?",
        "É a situação comunicativa em que estão inseridos o emissor e o receptor."
    ),
    (
        "O que é feedback?",
        "É a resposta do receptor ao emissor, que valida se a mensagem foi compreendida."
    ),
    (
        "Por que o feedback é importante?",
        "Porque sem retorno não há comunicação efectiva."
    ),
    (
        "O que é comunicação verbal?",
        "É a comunicação feita por meio da fala ou da escrita."
    ),
    (
        "O que é comunicação não-verbal?",
        "É a comunicação realizada através de gestos, expressões faciais, postura e linguagem corporal."
    ),
    (
        "O que é comunicação unilateral?",
        "É aquela em que apenas o emissor actua e o receptor é passivo, como na rádio e televisão."
    ),
    (
        "O que é comunicação bilateral?",
        "É a comunicação em que há troca de papéis entre emissor e receptor."
    ),
    (
        "Diferencie comunicação interpessoal de intrapessoal.",
        "A comunicação interpessoal ocorre entre duas ou mais pessoas, enquanto a intrapessoal acontece dentro do próprio indivíduo."
    ),
    (
        "O que é a função referencial da linguagem?",
        "É a função que tem como objectivo informar sobre algo de forma objetiva."
    ),
    (
        "O que caracteriza a função emotiva?",
        "A expressão de sentimentos, emoções e opiniões do emissor."
    ),
    (
        "Qual é a função apelativa da linguagem?",
        "É a função que procura convencer ou persuadir o receptor."
    ),
    (
        "O que é a função fática?",
        "É a função usada para estabelecer, manter ou interromper o contacto comunicativo."
    ),
    (
        "O que é a função metalinguística?",
        "É quando a linguagem fala sobre ela mesma, como nos dicionários e gramáticas."
    ),
    (
        "O que caracteriza o estilo de comunicação passivo?",
        "A dificuldade em se expressar e em defender as próprias ideias, evitando conflitos."
    ),
    (
        "O que caracteriza o estilo agressivo?",
        "A comunicação directa, dominante e pouco sensível aos sentimentos dos outros."
    ),
    (
        "O que é o estilo de comunicação manipulador?",
        "É aquele em que a pessoa expressa o descontentamento de forma indirecta."
    ),
    (
        "Qual é o estilo de comunicação ideal?",
        "O estilo assertivo."
    ),
    (
        "O que é comunicação assertiva?",
        "É a capacidade de expressar ideias com clareza, respeito e confiança, considerando os outros."
    ),
]

ADMIN_EMAIL = "admin@uni.ao"
ADMIN_PASSWORD = "admin123"

with app.app_context():
    db.create_all()

    # ✅ Criar ou actualizar admin (sempre consistente para defesa)
    admin = User.query.filter_by(email=ADMIN_EMAIL).first()

    if not admin:
        admin = User(
            full_name="Administrador",
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            is_admin=True
        )
        db.session.add(admin)
    else:
        admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
        admin.is_admin = True

    # Inserir Q/A se BD estiver vazia
    if QAItem.query.count() == 0:
        for q, a in SEED_QA:
            db.session.add(QAItem(question=q, answer=a))

    db.session.commit()

print("Seed concluído.")
print(f"Admin: {ADMIN_EMAIL} | Password: {ADMIN_PASSWORD}")
