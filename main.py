from flask import Flask
from flask import request, redirect, render_template
import socket
import hashlib
import validators

app = Flask(__name__)


def database(message):
    host = "127.0.0.1"
    port = 6379
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(message.encode())
    data = sock.recv(1024)
    sock.close()
    print(data)
    return data.decode('ASCII')


@app.route('/<name>')
def redirShort(name):
    if name == 'favicon.ico':
        return ''
    data = database("HGET " + name)
    print(data)
    if validators.url(data):
        return redirect(data, code=302)
    else:
        return render_template('error.html', message=data)


def createUrl(link):
    shlink = hashlib.sha1(link.encode()).hexdigest()
    while len(shlink) >= 6:
        req = "HSET " + shlink[:6] + " " + link
        ans = database(req)
        if ans == "Ok":
            return shlink[:6]
        else:
            return ans

    return "Мы не смогли бы этого сделать"


@app.route('/', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        link = request.form.get('link')
        if validators.url(link):
            ans = "http://127.0.0.1:5000/" + createUrl(link)
            return "<h2>Вот сокращенная ссылка, которую мы сделали для вас: {0}</h2>".format(ans)
        else:
            return render_template('error.html', message="Вы дали нам неверную ссылку")

    return render_template('glav.html')


if __name__ == '__main__':
    app.run(debug=True)
