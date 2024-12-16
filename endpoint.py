from flask import Flask, jsonify, request
import cx_Oracle
import datetime

app = Flask(__name__)

# Configurações de conexão com o Oracle
ORACLE_USERNAME = 'COBATA'
ORACLE_PASSWORD = 'C0BAT4D1T'
ORACLE_HOST = '192.168.0.254'
ORACLE_PORT = 1523
ORACLE_SID = 'WINT'  # SID do banco de dados

def get_oracle_data_paginated(data_inicial, data_final, offset, limit):
    try:
        # Criar o DSN (Data Source Name) para SID
        dsn = cx_Oracle.makedsn(ORACLE_HOST, ORACLE_PORT, sid=ORACLE_SID)

        # Conectar ao banco de dados Oracle
        connection = cx_Oracle.connect(ORACLE_USERNAME, ORACLE_PASSWORD, dsn)
        print("Conexão com o banco de dados bem-sucedida!")

        # Criar um cursor e executar a consulta com paginação usando ROW_NUMBER
        cursor = connection.cursor()

        query = """
            SELECT DESCRICAO, CODPROD, DATA, QT, PVENDA, VLCUSTOFIN
            FROM (
                SELECT DESCRICAO, CODPROD, DATA, QT, PVENDA, VLCUSTOFIN, 
                    ROW_NUMBER() OVER (ORDER BY DATA) AS row_num
                FROM VW_VENDASPEDIDO
                WHERE TRUNC(DATA) BETWEEN :data_inicial AND :data_final
            )
            WHERE row_num > :offset AND row_num <= :limit
        """

        # Calcular o offset corretamente
        offset_value = (offset - 1) * limit
        limit_value = offset * limit

        # Passar os parâmetros para a consulta
        params = {
            'data_inicial': data_inicial, 
            'data_final': data_final,
            'offset': offset_value,
            'limit': limit_value
        }

        # Executar a consulta com os parâmetros
        cursor.execute(query, params)

        # Obter resultados
        rows = cursor.fetchall()

        # Fechar o cursor e a conexão
        cursor.close()
        connection.close()

        return rows
    except cx_Oracle.DatabaseError as e:
        print(f"Ocorreu um erro ao conectar ou executar a consulta: {e}")
        return []

# Endpoint para acessar os dados com intervalo de datas e paginação
@app.route('/dados', methods=['GET'])
def get_data():
    # Obter os parâmetros de data da URL (no formato YYYY-MM-DD)
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')

    # Verificar se as datas foram fornecidas
    if not data_inicial_str or not data_final_str:
        return jsonify({"error": "Parâmetros de data_inicial e data_final são obrigatórios."}), 400

    # Pegar a página e limite
    pagina = int(request.args.get('pagina', 1))  # Padrão: página 1
    limite = int(request.args.get('limite', 1000))  # Padrão: limite 100

    try:
        # Converter as strings para objetos datetime
        data_inicial = datetime.datetime.strptime(data_inicial_str, "%Y-%m-%d").date()
        data_final = datetime.datetime.strptime(data_final_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato de data inválido. Use o formato YYYY-MM-DD."}), 400

    # Obter os dados do Oracle com os filtros de data e paginação
    rows = get_oracle_data_paginated(data_inicial, data_final, pagina, limite)

    # Verificar se existem resultados
    if not rows:
        return jsonify({"message": "Nenhum dado encontrado para o intervalo de datas fornecido."}), 404

    # Converter os resultados para uma lista de dicionários
    results = []
    for row in rows:
        results.append({
            'DESCRICAO': row[0],
            'CODPROD': row[1],
            'DATA': row[2].strftime('%Y-%m-%d') if isinstance(row[2], datetime.date) else row[2],
            'QT': row[3],
            'PVENDA': row[4],
            'VLCUSTOFIN': row[5]
        })

    # Retornar os dados como JSON
    return jsonify(results)

# Iniciar o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
