from flask import Flask, request, jsonify, render_template
from analizador import MyParser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods= ['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text')
    parser = MyParser()
    lexer = parser.lex_parse(text)
    result = parser.parse(text)

    formatted_result = []
    tokens = []

    # Inicia la posición del caracter
    current_position = 0
    
    for tok in lexer:
        formatted_result.append(f"Linea: {tok.lineno}, Tipo: {tok.type}, Valor: {tok.value}, Posición: {current_position}")
        tokens.append({'line': tok.lineno, 'type': tok.type, 'value': tok.value, 'pos': current_position})

        # Actualiza la posición actual del caracter
        current_position = tok.lexpos

    if result['errors_syntax'] or result['errors_semantic']:
        return jsonify({
            'formatted': "\n".join(formatted_result),
            'tokens_list': tokens,
            'error': result['errors_syntax'],
            'error_2': result['errors_semantic'],
            'parse_result': None
        })
    else:
        return jsonify({
            'formatted': "\n".join(formatted_result),
            'tokens_list': tokens,
            'parse_result': result['result']
        })


if __name__ == '__main__':
    app.run(debug=True)
