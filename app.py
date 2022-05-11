from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.xbvl6.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('main.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        #token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": username_receive,                           # 기본값 아이디

    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})






@app.route('/sc')
def sc():
    return render_template('index.html')

@app.route("/sc/schedule", methods=["POST"])
def schedule_post():
    schedule_receive = request.form['schedule_give']
    date_receive = request.form['date_give']

    schedule_list = list(db.schedules.find({}, {'_id': False}))
    count = len(schedule_list) + 1

    doc = {
        'num': count,
        'schedule': schedule_receive,
        'date': date_receive,
        'emoticon': '',
        'comment': '',
        'done': 0
    }

    db.schedules.insert_one(doc)

    return jsonify({'msg': '추가 완료!'})

@app.route("/sc/schedule/done", methods=["POST"])
def schedule_done():
    num_receive = request.form['num_give']
    db.schedules.update_one({'num': int(num_receive)},{'$set':{'done': 1}})
    return jsonify({'msg': '일정 완료!'})

@app.route("/sc/schedule/fix", methods=["POST"])
def schedule_fix():
    num_receive = request.form['num_give']

    db.schedules.update_one({'num': int(num_receive)},{'$set':{'done': 0}})
    return jsonify({'msg': '수정 완료!'})

@app.route("/sc/schedule/comment", methods=["POST"])
def comment_save():
    comment_receive = request.form['comment_give']
    emoticon_receive = request.form['emoticon_give']
    num_receive = request.form['num_give']

    db.schedules.update_one({'num': int(num_receive)}, {"$set" : {"comment":comment_receive}})
    db.schedules.update_one({'num': int(num_receive)}, {"$set": {"emoticon": emoticon_receive}})

    # db.schedules.update_one({'num': int(num_receive)}, { '$push' : { "comment": comment_receive,
    #      "emoticon": emoticon_receive}})
    # db.schedules.update({'num': int(num_receive)}, {'$push': {"comment": comment_receive}})

    return jsonify({'msg': '추가 완료!'})

@app.route("/sc/schedule", methods=["GET"])
def schedule_get():
    schedule_list = list(db.schedules.find({}, {'_id': False}))

    return jsonify({'schedules': schedule_list})



@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        date = request.form['id']
        if date != "":
            aa = list(db.hyukFan.find({}, {'_id': False}))
            aa = sorted(aa, key=lambda comment: comment['name'])
            lowList = []
            for comments in aa:
                if comments['name'] >= date:
                    break
                lowList.append(comments)

            firList = []
            secList = []
            thrList = []
            for i in range(len(lowList) - 1, 0, -1):
                if lowList[i]["name"] == lowList[-1]["name"]:
                    firList.append(lowList[i])
                elif lowList[i]["name"] == lowList[-1 - len(firList)]["name"]:
                    secList.append(lowList[i])
                elif lowList[i]["name"] == lowList[-1 - len(firList) - len(secList)]["name"]:
                    thrList.append(lowList[i])
                else:
                    break

            return render_template('test.html', firSchedule = firList, secSchedule = secList, thrSchedule = thrList)

    return render_template('test.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)