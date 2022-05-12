from pymongo import MongoClient
import jwt
import hashlib
import base64
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

        return render_template('/index.html')
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        #token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
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

@app.route('/logout', methods=['POST'])
def logout():
    return render_template('login.html')




@app.route('/sc')
def sc():
    return render_template('index.html')

@app.route("/sc/schedule", methods=["POST"])
def schedule_post():
    schedule_receive = request.form['schedule_give']
    date_receive = request.form['date_give']
    time_receive = request.form['time_give']
    date = date_receive[5:7] + date_receive[8:10]
    time = time_receive[:2] + time_receive[3:]
    tk = request.cookies.get('mytoken')
    id = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])['id']

    doc = {
        'id' : id,
        'time': time,
        'schedule': schedule_receive,
        'date': date,
        'emoticon': '',
        'comment': '',
        'done': 0
    }

    db.schedules.insert_one(doc)

    return jsonify({'msg': '추가 완료!'})

@app.route("/sc/schedule/done", methods=["POST"])
def schedule_done():

    time_receive = request.form['time_give']
    if len(time_receive) == 3:
        time_receive = oct(int(time_receive))
        time_receive = "0" + time_receive[2:]

    db.schedules.update_one({'time': time_receive}, {'$set': {'done': 1}})
    return jsonify({'msg': '일정 완료!'})

@app.route("/sc/schedule/fix", methods=["POST"])
def schedule_fix():
    time_receive = request.form['time_give']
    if len(time_receive) == 3:
        time_receive = oct(int(time_receive))
        time_receive = "0" + time_receive[2:]

    db.schedules.update_one({'time': time_receive}, {'$set': {'done': 0}})
    return jsonify({'msg': '수정 완료!'})

@app.route("/sc/schedule/comment", methods=["POST"])
def comment_save():
    comment_receive = request.form['comment_give']
    emoticon_receive = request.form['emoticon_give']
    time_receive = request.form['time_give']

    db.schedules.update_one({'time': time_receive}, {"$set" : {"comment": comment_receive}})
    db.schedules.update_one({'time': time_receive}, {"$set": {"emoticon": emoticon_receive}})

    return jsonify({'msg': '추가 완료!'})

@app.route("/sc/schedule", methods=["GET"])
def schedule_get():
    tk = request.cookies.get('mytoken')
    id = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])['id']

    date = datetime.now()
    date = str(date.month) + str(date.day)
    if len(date) == 3:
        date = "0" + date
    schedule_list = list(db.schedules.find({"id": id, "date": date}, {'_id': False}))
    schedule_list = sorted(schedule_list, key=lambda x: x['time'])
    return jsonify({'schedules': schedule_list})



@app.route('/beforeSC', methods=['POST', 'GET'])
def beforeSC():
    if request.method == 'POST':
        tk = request.cookies.get('mytoken')
        id = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])['id']

        date = request.form['id']
        if date != "":
            sList = list(db.schedules.find({"id": id}, {'_id': False}))
            schedule_list = sorted(sList, key=lambda x: x['id'])
            schedule_list = sorted(schedule_list, key=lambda x: x['date'])
            lowList = []

            #이전 날짜들의 스케쥴을 전부 저장
            for sche in schedule_list:
                if sche['date'] > date:
                    break
                lowList.append(sche)

            #print(lowList)

            firList = []
            secList = []
            thrList = []


            ##low list가 비어있는 상태
            if not lowList:
                return render_template('beforeSC.html')

            print(lowList)

            #date를 비교해가며 list들에 추가
            #무조건 한 리스트는 찰 수 밖에 없어서 예외처리 할 필요 없음
            for i in range(len(lowList) - 1, -1, -1):
                if lowList[i]["date"] == lowList[len(lowList) - 1]["date"]:
                    firList.append(lowList[i])
                elif lowList[i]["date"] != firList[0]["date"]:
                    secList.append(lowList[i])
                elif lowList[i]["date"] != secList[0]["date"]:
                    thrList.append(lowList[i])
                else:
                    break

            firList = sorted(firList, key=lambda x: x['time'])
            secList = sorted(secList, key=lambda x: x['time'])
            thrList = sorted(thrList, key=lambda x: x['time'])
            return render_template('beforeSC.html', firSchedule = firList,
                                   secSchedule = secList,
                                   thrSchedule = thrList)

    return render_template('beforeSC.html')




if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)