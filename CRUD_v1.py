from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)


# 数据库配置,默认用户为root
password=input("password:")
db_config = {
    'user': 'root',
    'password': password,
    'host': 'localhost',
    'database': 'movie_industry'
}

# 数据库连接函数
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/add_movie', methods=['POST'])
def add_movie():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(prepared=True)
    query = """
        CALL AddMovie(%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (data['Moviename'], data['Length'], data['Releaseyear'], data['PlotSummary'], data['ResourceLink'], data['ProductionCompanyID']))
        conn.commit()
        response = {'message': 'Movie added successfully!'}
        status_code = 201
    except mysql.connector.Error as err:
        response = {'error': str(err)}
        status_code = 400
    cursor.close()
    conn.close()
    return jsonify(response), status_code

@app.route('/update_movie/<int:id>', methods=['PUT'])
def update_movie(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(prepared=True)
    query = """
        CALL UpdateMovie(%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (id, data['Moviename'], data['Length'], data['Releaseyear'], data['PlotSummary'], data['ResourceLink'], data['ProductionCompanyID']))
        conn.commit()
        response = {'message': 'Movie updated successfully!'}
        status_code = 200
    except mysql.connector.Error as err:
        response = {'error': str(err)}
        status_code = 400
    cursor.close()
    conn.close()
    return jsonify(response), status_code

@app.route('/delete_movie/<int:id>', methods=['DELETE'])
def delete_movie(id):
    conn = get_db_connection()
    cursor = conn.cursor(prepared=True)
    query = """
        CALL DeleteMovie(%s)
    """
    try:
        cursor.execute(query, (id,))
        conn.commit()
        response = {'message': 'Movie deleted successfully!'}
        status_code = 200
    except mysql.connector.Error as err:
        response = {'error': str(err)}
        status_code = 400
    cursor.close()
    conn.close()
    return jsonify(response), status_code

if __name__ == '__main__':
    app.run(debug=True)
