"""
Web interface module for ErrorTrace Pro
"""
import os
import sys
import json
import traceback
from flask import Flask, render_template, request, jsonify

import errortrace_pro

def create_app():
    """Create and configure a Flask app for ErrorTrace Pro web interface"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "errortrace-dev-key")
    
    # Initialize ErrorTrace Pro
    handler = errortrace_pro.init(
        enable_suggestions=True,
        colored_output=True,
        verbose=True
    )
    
    @app.route('/')
    def index():
        """Render the main page"""
        return render_template('index.html')
    
    @app.route('/execute', methods=['POST'])
    def execute():
        """Execute Python code and catch errors with ErrorTrace Pro"""
        code = request.json.get('code', '')
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'No code provided'
            })
        
        # Create a local namespace for execution
        local_vars = {}
        
        try:
            # Execute the code
            exec(code, globals(), local_vars)
            
            # Get any output variables
            output_vars = {k: str(v) for k, v in local_vars.items() 
                        if not k.startswith('_') and k != 'builtins'}
            
            return jsonify({
                'success': True,
                'result': 'Code executed successfully',
                'variables': output_vars
            })
            
        except Exception:
            # Get exception info
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Get the formatted traceback from ErrorTrace Pro
            visual_traceback = handler.visualizer.format_traceback(exc_type, exc_value, exc_traceback)
            
            # Get solution suggestions
            solutions = handler.solution_provider.get_solutions(
                exc_type, exc_value, 
                handler._get_error_context(exc_type, exc_value, exc_traceback)
            )
            
            # Return the error information
            return jsonify({
                'success': False,
                'error_type': exc_type.__name__,
                'error_message': str(exc_value),
                'traceback': visual_traceback,
                'solutions': solutions
            })
    
    @app.route('/examples')
    def examples():
        """Return example code snippets"""
        examples = {
            'examples': [
                {
                    'title': 'ZeroDivisionError',
                    'code': 'def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)'
                },
                {
                    'title': 'KeyError',
                    'code': 'data = {"name": "ErrorTrace Pro", "version": "0.1.0"}\nresult = data["nonexistent_key"]'
                },
                {
                    'title': 'TypeError',
                    'code': 'result = "ErrorTrace Pro" + 42'
                },
                {
                    'title': 'AttributeError',
                    'code': 'value = "ErrorTrace Pro"\nresult = value.nonexistent_method()'
                },
                {
                    'title': 'IndexError',
                    'code': 'my_list = [1, 2, 3]\nresult = my_list[10]'
                },
                {
                    'title': 'NameError',
                    'code': 'result = undefined_variable * 10'
                },
                {
                    'title': 'RecursionError',
                    'code': 'def recursive_function(n):\n    if n == 0:\n        return 0\n    else:\n        # Mistake: no decreasing n\n        return recursive_function(n)\n\nresult = recursive_function(10)'
                }
            ]
        }
        
        return jsonify(examples)
    
    return app