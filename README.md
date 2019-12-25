![](https://i.imgur.com/Ez57Azt.png)

Curve is a framework for creating web applications. Designed to be fast and easy, with the ability to scale to complex applications.

## Example
```python
  from curve import Curve, init_server

  app = Curve()


  @app.route('/')
  def route_index():
      return app.response.send('Welcome to Curve HTTP Server')


  init_server(app = app,
      module = __name__,
      port = 80,
      address = '127.0.0.1')
```
