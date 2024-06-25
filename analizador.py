import ply.lex as lex
import ply.yacc as yacc
import sys

class MyParser:
    def __init__(self):
        self.errors_syntax = []
        self.errors_semantic = []
        self.variables = {}
        self.lexer = self.build_lexer()
        self.parser = self.build_parser()

    # Definición de tokens
    tokens = (
        'INT', 'FLOAT', 'STRING', 'IF', 'WHILE', 'FOR', 'IN', 'RANGE', 'INPUT', 'RETURN',
        'ID', 'NUMBER', 'DECIMAL', 'TEXT', 'INCLUDE',
        'ASSIGN', 'EQ', 'GT', 'LT', 'LE', 'PLUS', 'AND', 'PLUS_OP', 'MINUS_OP', 'MULT_OP', 'DIV_OP',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA', 'HEADER'
    )

    # Definiciones de expresiones regulares para tokens simples
    t_ASSIGN = r'='
    t_EQ = r'=='
    t_GT = r'>'
    t_LT = r'<'
    t_LE = r'<='
    t_PLUS = r'\+\+'
    t_PLUS_OP = r'\+'
    t_MINUS_OP = r'-'
    t_MULT_OP = r'\*'
    t_DIV_OP = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMICOLON = r';'
    t_COMMA = r','

    # Definiciones de palabras reservadas
    reserved = {
        'INT': 'INT',
        'FLOAT': 'FLOAT',
        'STRING': 'STRING',
        'IF': 'IF',
        'WHILE': 'WHILE',
        'FOR': 'FOR',
        'IN': 'IN',
        'RANGE': 'RANGE',
        'INPUT': 'INPUT',
        'AND': 'AND',
        'DO': 'DO',
        'ENDDO': 'ENDDO',
        'ENDWHILE': 'ENDWHILE',
        'RETURN': 'RETURN',
        'include': 'INCLUDE'
    }

    # Definiciones de tokens complejos
    def t_INCLUDE(self, t):
        r'\#include'
        return t

    def t_HEADER(self, t):
        r'\<[a-zA-Z0-9_\.]+\>'
        return t
    
    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')  # Verifica si es una palabra reservada
        return t

    def t_DECIMAL(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_TEXT(self, t):
        r'\".*?\"'
        t.value = str(t.value)
        return t

    # Ignorar espacios y tabulaciones
    t_ignore = ' \t'

    # Manejo de saltos de línea
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    # Manejador de errores léxicos
    def t_error(self, t):
        self.errors_syntax.append(f"Error léxico en '{t.value[0]}' en la línea {t.lineno}, posición {t.lexpos}")
        t.lexer.skip(1)

    def build_lexer(self):
        return lex.lex(module=self)

    # Definición de la precedencia y asociaciones
    precedence = (
        ('left', 'PLUS_OP', 'MINUS_OP'),
        ('left', 'MULT_OP', 'DIV_OP'),
    )

    # Definición de la gramática
    def p_program(self, p):
        '''program : includes statements'''
        p[0] = ('program', p[1])

    def p_statements(self, p):
        '''statements : statement
                      | statement statements'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
    
    def p_includes(self, p):
        '''includes : include
                    | include includes'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
    
    def p_include(self, p):
        '''include : INCLUDE HEADER'''
        p[0] = ('include', p[2])

    def p_statement(self, p):
        '''statement : declaration
                     | assignment
                     | if_statement
                     | for_statement
                     | increment_statement
                     | return_statement
                     | function_definition'''
        p[0] = p[1]

    def p_declaration(self, p):
        '''declaration : INT ID ASSIGN expression SEMICOLON
                       | FLOAT ID ASSIGN expression SEMICOLON
                       | STRING ID ASSIGN TEXT SEMICOLON'''
        if p[1] == 'INT' and isinstance(p[4], int):
            self.variables[p[2]] = ('int', p[4])
        elif p[1] == 'FLOAT' and (isinstance(p[4], float) or isinstance(p[4], int)):
            self.variables[p[2]] = ('float', float(p[4]))
        elif p[1] == 'STRING' and isinstance(p[4], str):
            self.variables[p[2]] = ('string', p[4])
        else:
            self.errors_semantic.append(f"Error semántico en la línea {p.lineno(1)}, posición {p.lexpos(1)}: {p[2]} debe ser del tipo {p[1]}")
        p[0] = ('declaration', p[1], p[2], p[4])

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expression SEMICOLON'''
        if p[1] not in self.variables:
            self.errors_semantic.append(f"Error semántico: Variable '{p[1]}' no ha sido declarada.")
        else:
            var_type, _ = self.variables[p[1]]
            if isinstance(p[3], float) and var_type != 'float':
                self.errors_semantic.append(f"Error semántico: Tipo incorrecto para asignación a '{p[1]}'. Se esperaba '{var_type}'.")
            elif isinstance(p[3], int) and var_type != 'int':
                self.errors_semantic.append(f"Error semántico: Tipo incorrecto para asignación a '{p[1]}'. Se esperaba '{var_type}'.")
            elif isinstance(p[3], str) and var_type != 'string':
                self.errors_semantic.append(f"Error semántico: Tipo incorrecto para asignación a '{p[1]}'. Se esperaba '{var_type}'.")
            else:
                self.variables[p[1]] = (var_type, p[3])
        p[0] = ('assignment', p[1], p[3])

    def p_if_statement(self, p):
        '''if_statement : IF LPAREN condition RPAREN LBRACE statements RBRACE'''
        p[0] = ('if', p[3], p[6])

    def p_for_statement(self, p):
        '''for_statement : FOR LPAREN assignment condition SEMICOLON increment_statement RPAREN LBRACE statements RBRACE'''
        p[0] = ('for', p[3], p[4], p[5], p[8])
    
    def p_condition(self, p):
        '''condition : expression EQ expression
                     | expression GT expression
                     | expression LT expression
                     | expression LE expression
                     | condition AND condition'''
        if p[2] == 'AND':
            p[0] = ('and', p[1], p[3])
        else:
            p[0] = ('condition', p[2], p[1], p[3])

    def p_expression(self, p):
        '''expression : NUMBER
                      | DECIMAL
                      | ID
                      | expression PLUS_OP expression
                      | expression MINUS_OP expression
                      | expression MULT_OP expression
                      | expression DIV_OP expression'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ('op', p[2], p[1], p[3])

    def p_increment_statement(self, p):
        '''increment_statement : ID PLUS
                               | ID PLUS SEMICOLON'''
        if p[1] not in self.variables or self.variables[p[1]][0] != 'int':
            self.errors_semantic.append(f"Error semántico en la línea {p.lineno(1)}, posición {p.lexpos(1)}: {p[1]} debe ser una variable entera")
        else:
            self.variables[p[1]] = ('int', self.variables[p[1]][1] + 1)
        p[0] = ('increment', p[1])
    
    def p_return_statement(self, p):
        '''return_statement : RETURN expression SEMICOLON'''
        p[0] = ('return', p[2])

    def p_function_definition(self, p):
        '''function_definition : INT ID LPAREN RPAREN LBRACE statements RBRACE'''
        p[0] = ('function', p[2], p[6])

    def p_error(self, p):
        if p:
            self.errors_syntax.append(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}, posición {p.lexpos}")
        else:
            self.errors_syntax.append("Error de sintaxis en EOF - se esperaba más código o una estructura de bloque está incompleta")

    def build_parser(self):
        return yacc.yacc(module=self)

    def lex_parse(self, data):
        self.lexer.input(data)
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens

    def parse(self, data):
        self.errors_syntax = []
        self.errors_semantic = []
        self.variables = {}
        result = self.parser.parse(data)

        if self.errors_syntax:
            print("\nErrores sintácticos:")
            print("\n".join(self.errors_syntax))

        if self.errors_semantic:
            print("\nErrores semánticos:")
            print("\n".join(self.errors_semantic))

        print("\nResultado del análisis sintáctico:")
        print(result)

        return {
            'errors_syntax': self.errors_syntax,
            'errors_semantic': self.errors_semantic,
            'result': result
        }

if __name__ == "__main__":
    parser = MyParser()

    data = '''
    #include <stdio.h>

    INT main(){
        INT z=10; 
        INT val=10;
        INT suma=10;

        FOR(z = 1; z <= 10; z++){
            val=10;
            suma=suma+val;
        }

        RETURN 1;
        }
    '''

    result = parser.parse(data)
    lexer = parser.lex_parse(data)
    for token in lexer:
        print(token)

    print("esto es el result :", result)
