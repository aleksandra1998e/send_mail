from flask import Flask, request, render_template, flash, redirect, url_for
from celery import Celery
from datetime import datetime
from sending import send

app = Flask(__name__, template_folder='templates')
app.config['CELERY_BROKER_URL'] = 'localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'localhost:6379/0'

client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)


@client.task
def send_mail(data):
    send(
        data['email'],
        data['password'],
        data['message'],
        data['topic'],
        data['name'],
        data['surname'],
        data['birthday']
    )


@app.route('/opened/<mail>', methods=['GET'])
def opened(mail):
    with open('delivery.txt', 'a') as f:
        f.write("{} was opened {}\n".format(mail, datetime.now()))
    return '', 200


@app.route('/', methods=['GET', 'POST'])
def sending_with_a_delay():
    if request.method == 'GET':
        return render_template('form.html')

    elif request.method == 'POST':
        data = {'name': False, 'surname': False, 'birthday': False}
        data['email'] = request.form['email']
        data['password'] = request.form['password']
        data['topic'] = request.form['topic']
        data['message'] = request.form['message']
        duration = int(request.form['duration'])
        duration_unit = request.form['duration_unit']

        if duration_unit == 'minutes':
            duration *= 60
        elif duration_unit == 'hours':
            duration *= 3600
        elif duration_unit == 'days':
            duration *= 86400

        if request.form.get('name'):
            data['name'] = True
        if request.form.get('surname'):
            data['surname'] = True
        if request.form.get('birthday'):
            data['birthday'] = True

        send_mail.apply_async(args=[data], countdown=duration)
        mes = 'Email will be sent to {email} in {duration} {duration_unit}'.format(email=data["email"],
                                                                                   duration=request.form["duration"],
                                                                                   duration_unit=duration_unit)
        flash(mes)

        return redirect(url_for('sending_with_a_delay'))


if __name__ == '__main__':
    app.run(debug=True)
