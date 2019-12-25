from curve import Curve, init_server

app = Curve()


@app.route('/')
def route_index():
    return app.response.send('Welcome to Curve HTTP Server')


init_server(app = app,
		module = __name__,
		port = 80,
		address = '127.0.0.1')