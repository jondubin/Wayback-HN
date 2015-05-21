from flask import render_template


def invalid_input_decorator(func):
    def func_wrapper(*args):
        try:
            func(*args)
        except ValueError:
            return render_template('invalid_input.html')
    return func_wrapper
