from JackTokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self, input_file_path, output_path):
        """
        Initialize the compilation engine
        :param input_file_path: Path to the input .jack file
        :param output_path: Path to the output .xml file
        """
        self.indent_level = 0
        try:
            self.tokenizer = JackTokenizer(input_file_path)
            # If no tokens, raise an error
            if self.tokenizer.tokenLength == 0:
                raise Exception(f"Input file {input_file_path} appears to be empty")
            # Prime the tokenizer with the first token
            # (Note: We already set currentToken to the 1st token in JackTokenizer)
        except Exception as e:
            raise Exception(f"Failed to initialize tokenizer: {str(e)}")

        try:
            self.output = open(output_path, "w+")
        except Exception as e:
            raise Exception(f"Failed to open output file {output_path}: {str(e)}")

    def close(self):
        """Explicitly close the output file"""
        if hasattr(self, 'output') and self.output:
            self.output.flush()
            self.output.close()

    def write_element(self, tag, value):
        """Writes an XML element with the given tag and value."""
        indent = '  ' * self.indent_level
        self.output.write(f'{indent}<{tag}> {value} </{tag}>\n')
        self.output.flush()  # Force write to disk

    def write_xml_tag(self, tag):
        """Writes an XML tag, handling indentation for nested structures."""
        if tag.startswith('/'):  # closing tag
            self.indent_level -= 1
            indent = '  ' * self.indent_level
            self.output.write(f'{indent}<{tag}>\n')
        else:
            indent = '  ' * self.indent_level
            self.output.write(f'{indent}<{tag}>\n')
            self.indent_level += 1
        self.output.flush()

    def write_current_token(self):
        """Writes the current token to the output file with appropriate XML tags."""
        token_type = self.tokenizer.token_type()
        if token_type == 'KEYWORD':
            self.write_element('keyword', self.tokenizer.keyWord())
        elif token_type == 'SYMBOL':
            symbol = self.tokenizer.symbol()
            # Escape special XML characters
            if symbol == '<':
                symbol = '&lt;'
            elif symbol == '>':
                symbol = '&gt;'
            elif symbol == '&':
                symbol = '&amp;'
            self.write_element('symbol', symbol)
        elif token_type == 'IDENTIFIER':
            self.write_element('identifier', self.tokenizer.identifier())
        elif token_type == 'INT_CONST':
            self.write_element('integerConstant', str(self.tokenizer.intVal()))
        elif token_type == 'STRING_CONST':
            self.write_element('stringConstant', self.tokenizer.stringVal())

    # ------------------------------
    # Compilation Methods
    # ------------------------------

    def compile_class(self):
        """Compiles a complete class."""
        # Expect the current token to be 'class'
        if self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyWord() == 'class':
            self.write_xml_tag('class')
            # Write 'class'
            self.write_current_token()
            self.tokenizer.advance()

            # Class name (identifier)
            if self.tokenizer.token_type() == 'IDENTIFIER':
                self.write_current_token()
                self.tokenizer.advance()

                # Opening brace '{'
                if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '{':
                    self.write_current_token()
                    self.tokenizer.advance()

                    # Compile class var declarations and subroutines
                    while self.tokenizer.token_type() == 'KEYWORD':
                        if self.tokenizer.keyWord() in ['static', 'field']:
                            self.compile_class_var_dec()
                        elif self.tokenizer.keyWord() in ['constructor', 'function', 'method']:
                            self.compile_subroutine()
                        else:
                            break

                    # Closing brace '}'
                    if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
                        self.write_current_token()

            self.write_xml_tag('/class')

    def compile_class_var_dec(self):
        """Compiles a static variable declaration or field declaration."""
        self.write_xml_tag('classVarDec')

        # 'static' or 'field'
        self.write_current_token()
        self.tokenizer.advance()

        # type (int, char, boolean, or className)
        self.write_current_token()
        self.tokenizer.advance()

        # varName (possibly multiple, comma-separated)
        while True:
            self.write_current_token()
            self.tokenizer.advance()

            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.write_current_token()
                self.tokenizer.advance()
            else:
                break

        # Semicolon
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/classVarDec')

    def compile_subroutine(self):
        """Compiles a complete subroutine (constructor, function, or method)."""
        self.write_xml_tag('subroutineDec')

        # constructor / function / method
        self.write_current_token()
        self.tokenizer.advance()

        # return type (void or type)
        self.write_current_token()
        self.tokenizer.advance()

        # subroutine name
        self.write_current_token()
        self.tokenizer.advance()

        # parameter list
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_parameter_list()
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
                self.write_current_token()
                self.tokenizer.advance()

        # subroutine body
        self.compile_subroutine_body()

        self.write_xml_tag('/subroutineDec')

    def compile_parameter_list(self):
        """Compiles a (possibly empty) parameter list."""
        self.write_xml_tag('parameterList')

        while not (self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self.write_current_token()
            self.tokenizer.advance()
            # If comma, continue
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.write_current_token()
                self.tokenizer.advance()

        self.write_xml_tag('/parameterList')

    def compile_subroutine_body(self):
        """Compiles a subroutine body: { varDec* statements }"""
        self.write_xml_tag('subroutineBody')

        # Expect '{'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '{':
            self.write_current_token()
            self.tokenizer.advance()

            # varDec*
            while self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyWord() == 'var':
                self.compile_var_dec()

            # statements
            self.compile_statements()

            # '}'
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
                self.write_current_token()
                self.tokenizer.advance()

        self.write_xml_tag('/subroutineBody')

    def compile_var_dec(self):
        """Compiles a var declaration: var type varName (',' varName)* ';'"""
        self.write_xml_tag('varDec')

        # 'var'
        self.write_current_token()
        self.tokenizer.advance()

        # type
        self.write_current_token()
        self.tokenizer.advance()

        # varName (possibly multiple)
        while True:
            self.write_current_token()
            self.tokenizer.advance()

            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.write_current_token()
                self.tokenizer.advance()
            else:
                break

        # ';'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/varDec')

    def compile_statements(self):
        """Compiles a sequence of statements."""
        self.write_xml_tag('statements')

        while self.tokenizer.token_type() == 'KEYWORD':
            kw = self.tokenizer.keyWord()
            if kw == 'let':
                self.compile_let()
            elif kw == 'if':
                self.compile_if()
            elif kw == 'while':
                self.compile_while()
            elif kw == 'do':
                self.compile_do()
            elif kw == 'return':
                self.compile_return()
            else:
                break

        self.write_xml_tag('/statements')

    def compile_let(self):
        """Compiles a let statement: let varName ('[' expression ']')? = expression ;"""
        self.write_xml_tag('letStatement')

        # 'let'
        self.write_current_token()
        self.tokenizer.advance()

        # varName
        self.write_current_token()
        self.tokenizer.advance()

        # Optional array indexing
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '[':
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_expression()
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ']':
                self.write_current_token()
                self.tokenizer.advance()

        # '='
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '=':
            self.write_current_token()
            self.tokenizer.advance()

        # expression
        self.compile_expression()

        # ';'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/letStatement')

    def compile_if(self):
        """Compiles an if statement: if ( expression ) { statements } (else { statements })?"""
        self.write_xml_tag('ifStatement')

        # 'if'
        self.write_current_token()
        self.tokenizer.advance()

        # '('
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.write_current_token()
            self.tokenizer.advance()

        # expression
        self.compile_expression()

        # ')'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
            self.write_current_token()
            self.tokenizer.advance()

        # '{'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '{':
            self.write_current_token()
            self.tokenizer.advance()

        # statements
        self.compile_statements()

        # '}'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
            self.write_current_token()
            self.tokenizer.advance()

        # optional else
        if self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyWord() == 'else':
            self.write_current_token()
            self.tokenizer.advance()

            # '{'
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '{':
                self.write_current_token()
                self.tokenizer.advance()

            # statements
            self.compile_statements()

            # '}'
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
                self.write_current_token()
                self.tokenizer.advance()

        self.write_xml_tag('/ifStatement')

    def compile_while(self):
        """Compiles a while statement: while ( expression ) { statements }"""
        self.write_xml_tag('whileStatement')

        # 'while'
        self.write_current_token()
        self.tokenizer.advance()

        # '('
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.write_current_token()
            self.tokenizer.advance()

        # expression
        self.compile_expression()

        # ')'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
            self.write_current_token()
            self.tokenizer.advance()

        # '{'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '{':
            self.write_current_token()
            self.tokenizer.advance()

        # statements
        self.compile_statements()

        # '}'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/whileStatement')

    def compile_do(self):
        """Compiles a do statement: do subroutineCall ;"""
        self.write_xml_tag('doStatement')

        # 'do'
        self.write_current_token()
        self.tokenizer.advance()

        # subroutine call => identifier [( '.' identifier )] '(' expressionList ')'
        self.write_current_token()  # identifier
        self.tokenizer.advance()

        # Possibly a '.' and another identifier
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '.':
            self.write_current_token()
            self.tokenizer.advance()
            if self.tokenizer.token_type() == 'IDENTIFIER':
                self.write_current_token()
                self.tokenizer.advance()

        # '('
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_expression_list()
            # ')'
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
                self.write_current_token()
                self.tokenizer.advance()

        # ';'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/doStatement')

    def compile_return(self):
        """Compiles a return statement: return expression? ;"""
        self.write_xml_tag('returnStatement')

        # 'return'
        self.write_current_token()
        self.tokenizer.advance()

        # optional expression
        if not (self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.compile_expression()

        # ';'
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ';':
            self.write_current_token()
            self.tokenizer.advance()

        self.write_xml_tag('/returnStatement')

    def compile_expression(self):
        """Compiles an expression: term (op term)*"""
        self.write_xml_tag('expression')
        self.compile_term()

        # while next token is an operator, keep compiling terms
        while (self.tokenizer.token_type() == 'SYMBOL'
               and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']):
            self.write_current_token()
            self.tokenizer.advance()
            self.compile_term()

        self.write_xml_tag('/expression')

    def compile_term(self):
        """Compiles a term. This routine is slightly complex due to variety of term types."""
        self.write_xml_tag('term')

        token_type = self.tokenizer.token_type()

        if token_type == 'INT_CONST':
            self.write_current_token()
            self.tokenizer.advance()

        elif token_type == 'STRING_CONST':
            self.write_current_token()
            self.tokenizer.advance()

        elif token_type == 'KEYWORD' and self.tokenizer.keyWord() in ['true', 'false', 'null', 'this']:
            self.write_current_token()
            self.tokenizer.advance()

        elif token_type == 'IDENTIFIER':
            # Could be varName, array access, or subroutine call
            self.write_current_token()
            self.tokenizer.advance()

            if self.tokenizer.token_type() == 'SYMBOL':
                if self.tokenizer.symbol() == '[':  # array access
                    self.write_current_token()
                    self.tokenizer.advance()
                    self.compile_expression()
                    if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ']':
                        self.write_current_token()
                        self.tokenizer.advance()
                elif self.tokenizer.symbol() in ['(', '.']:  # subroutine call
                    self.compile_subroutine_call_continuation()

        elif token_type == 'SYMBOL':
            if self.tokenizer.symbol() == '(':
                self.write_current_token()
                self.tokenizer.advance()
                self.compile_expression()
                if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
                    self.write_current_token()
                    self.tokenizer.advance()
            elif self.tokenizer.symbol() in ['-', '~']:  # unary op
                self.write_current_token()
                self.tokenizer.advance()
                self.compile_term()

        self.write_xml_tag('/term')

    def compile_subroutine_call_continuation(self):
        """
        Handles the remainder of a subroutine call after we've already
        read the first identifier (could be className or varName).
        """
        if self.tokenizer.token_type() == 'SYMBOL':
            if self.tokenizer.symbol() == '.':
                self.write_current_token()
                self.tokenizer.advance()
                # subroutine name
                if self.tokenizer.token_type() == 'IDENTIFIER':
                    self.write_current_token()
                    self.tokenizer.advance()

            if self.tokenizer.symbol() == '(':
                self.write_current_token()
                self.tokenizer.advance()
                self.compile_expression_list()
                if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')':
                    self.write_current_token()
                    self.tokenizer.advance()

    def compile_expression_list(self):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.write_xml_tag('expressionList')
        # If next token is not ')', compile first expression
        if not (self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self.compile_expression()

            # while comma, compile next expression
            while self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.write_current_token()
                self.tokenizer.advance()
                self.compile_expression()

        self.write_xml_tag('/expressionList')