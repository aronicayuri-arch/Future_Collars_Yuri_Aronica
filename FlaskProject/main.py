from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    my_list = ["aaa", "bbb", "ccc", "ddd", "eee"]
    return render_template("index.html", my_list=my_list)


@app.route('/hello/<name>/')
def hello(name):
    # return "Hello {}".format(name)
    return render_template("index.html", name=name)


@app.route('/myform/', methods=["GET", "POST"])
def get_data():
    print("Reading data")
    print("Name: " + request.form["form_name"])
    print("Lastname: " + request.form["form_lastname"])
    return "Success"


if __name__ == "__main__":
    app.run()
