import pandas as pd
import ast, json
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import csv

# Ler json válido
with open('databases/json/json_fixed.json', encoding='utf-8') as valid_json:

    data = json.loads(valid_json.read())

# Configurando o Pandas para nao ter limite de saída nos prints
pd.set_option('display.max_rows', None)

# Processando os dados com pandas
df = pd.json_normalize(data)

# Lendo CSV de referencia
r_df = pd.read_csv('databases/reference/NetEngine_F2A_V800R023C10SPC500_log_reference.csv',
                   on_bad_lines='skip',
                   encoding='utf-8',
                   quoting=csv.QUOTE_NONE,
                   engine='python',
                   sep=';')

# Definindo somente duas colunas para trabalho
pre_proc_r_df = r_df[['Log Level','Log Name']]

# Limpando os dados para que possamos ter somente os levels e name
pre_proc_r_df = pre_proc_r_df[pre_proc_r_df['Log Level'].fillna('').str.strip().str.isdigit()]

# Filtrando apenas log level maior que 4
pre_proc_r_df['level'] = pd.to_numeric(pre_proc_r_df['Log Level'], errors='coerce')
filtered_pre_proc_r_df = pre_proc_r_df[pre_proc_r_df['level'] > 5]
print(filtered_pre_proc_r_df)

# Criando uma lista de termos à serem desconsiderados na analise
termos_irrelevantes = []

for name in filtered_pre_proc_r_df['Log Name']:
    termos_irrelevantes.append(name)

regex_para_termos_irrelevantes = '|'.join(termos_irrelevantes)

df = df[~df['event_type'].str.contains(regex_para_termos_irrelevantes, na=False, case=False)]

# Event type interessantes
int_event_type = ["LOGIN", "LOGOUT", "SSH", "IM_LOGFILE_AGING_DELETE", "IP_UNLOCKED"]
regex_int_event_type = '|'.join(int_event_type)

# Aplicando ffiltro de termos interessantes
df = df[df['event_type'].str.contains(regex_int_event_type, na=False, case=False)]

# Equipamentos envolvidos
equitos_envolvidos = ["WAN-RJ-CIR-02", "WAN-RJ-CIR-01"]

# Filtrando por equipamentos
df = df[df['hostname'].isin(equitos_envolvidos)]

# Contando os dados por event_type
logs_por_tempo = df.dropna(subset=['@timestamp'])
valores_por_event_type = df['event_type'].value_counts()
print(f"Valores por Event type: {valores_por_event_type}\n")

# Contando os logs por timestamp
valores_por_timestamp = df['@timestamp'].value_counts()

# Moda dos logs
moda_logs = valores_por_timestamp.mode()[0]

# Filtrando apenas os timestamps com valor maior que a moda
timestamps_filtrados = valores_por_timestamp[valores_por_timestamp > moda_logs].index

# Aplicando o filtro
logs_por_tempo = logs_por_tempo[logs_por_tempo['@timestamp'].isin(timestamps_filtrados)]


# Plotando gráfico de ocorrencias por timestamp
plt.figure(figsize=(12,6))
sns.histplot(logs_por_tempo['@timestamp'], bins=50, kde=False, color='red')

plt.title('Distriuição de Eventos por Timestamp')
plt.xlabel('Tempo')
plt.ylabel('Contagem de eventos')
plt.xticks(rotation=90)
plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.tight_layout()

plt.show()
