from ooiservices import app

if __name__ == '__main__':
    app.run(port=4000, debug=True)

@app.route('/')
def root(name=None):
    if name:
        return render_template(name, title = "")
    else:
        return render_template("test.html", title = 'Main')