import sqlite3 as sql
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

banco = sql.connect("Banco de dados.db")
cursor = banco.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS dados(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     data_venda DATE,
     produto TEXT,
     categoria TEXT,
     valor_venda REAL
)""")

cursor.execute("""
INSERT INTO 
dados (data_venda,produto,categoria,valor_venda)
VALUES 
('2023-01-01', 'Produto A', 'Eletrônicos', 1500.00),
('2023-01-05', 'Produto B', 'Roupas', 350.00),
('2023-02-10', 'Produto C', 'Eletrônicos', 1200.00),
('2023-03-15', 'Produto D', 'Livros', 200.00),
('2023-03-20', 'Produto E', 'Eletrônicos', 800.00),
('2023-04-02', 'Produto F', 'Roupas', 400.00),
('2023-05-05', 'Produto G', 'Livros', 150.00),
('2023-06-10', 'Produto H', 'Eletrônicos', 1000.00),
('2023-07-20', 'Produto I', 'Roupas', 600.00),
('2023-08-25', 'Produto J', 'Eletrônicos', 700.00),
('2023-09-30', 'Produto K', 'Livros', 300.00),
('2023-10-05', 'Produto L', 'Roupas', 450.00),
('2023-11-15', 'Produto M', 'Eletrônicos', 900.00),
('2023-12-20', 'Produto N', 'Livros', 250.00);
""")

banco.commit()

df_vendas = pd.read_sql(
    "SELECT data_venda,produto,categoria,valor_venda FROM dados",
    banco,
)

sns.set_style("whitegrid")

print("Qual categoria deseja ver?")
print("1 - Eletrônicos \n2 - Livros \n3 - Roupas\n")
categoria = int(input("Qual categoria deseja ver? "))

# Mini filtragem para pegar a categoria que desejar análisar
j = ""
if categoria == 1:
    j = "Eletrônicos"
elif categoria == 2:
    j = "Livros"
elif categoria == 3:
    j = "Roupas"


# Um for para criar a coluna Mês, pegando os caracteres 5 e 6 da coluna 'data_venda'
# O motivo foi por os valores estarem como string quando olhamos .info()
for i in df_vendas.index:
    df_vendas.loc[i, "Mês"] = df_vendas["data_venda"][i][5:7]


# Soma de todas as vendas e um print mostrando esse valor como faturamento
anual = df_vendas["valor_venda"].sum()
print(f"Ao final do ano de 2023, a loja obteve um faturamento total de R$ {anual}")


# Um grafico de barra para mostrar o valor das vendas por mês, com o seaborn
# E com funções do pyplot para mudar o nome dos campos y e x
sns.barplot(data=df_vendas, x="Mês", y="valor_venda", hue="categoria").set(
    title="Vendas no ano de 2023"
)
plt.ylabel("Valor de vendas\n")
plt.xlabel("\nMês")


# Um grafico de linha para mostrar as vendas de cada produto por mês vendido
tabela = df_vendas.groupby("categoria").get_group(j)
tabela.plot("Mês", title=f"Vendas de {j} / M", grid=True, figsize=(7, 4))


# Uma Series com a soma de todas as vendas feita ao ano, por categoria
tabela = (
    df_vendas.groupby("categoria")
    .sum(numeric_only=True)
    .sort_values("valor_venda", ascending=False)
)
tabela
