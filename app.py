from flask import Flask, render_template, request, jsonify
app = Flask(__name__)


from pymongo import MongoClient
# client = MongoClient('mongodb+srv://test:sparta@cluster0.vrvtw.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db = client.dbsparta

client = MongoClient('mongodb+srv://test:sparta@cluster0.xbvl6.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/schedule", methods=["POST"])
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

@app.route("/schedule/done", methods=["POST"])
def schedule_done():
    num_receive = request.form['num_give']
    db.schedules.update_one({'num': int(num_receive)},{'$set':{'done': 1}})
    return jsonify({'msg': '일정 완료!'})

@app.route("/schedule/fix", methods=["POST"])
def schedule_fix():
    num_receive = request.form['num_give']

    db.schedules.update_one({'num': int(num_receive)},{'$set':{'done': 0}})
    return jsonify({'msg': '수정 완료!'})

@app.route("/schedule/comment", methods=["POST"])
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

@app.route("/schedule", methods=["GET"])
def schedule_get():
    schedule_list = list(db.schedules.find({}, {'_id': False}))

    return jsonify({'schedules': schedule_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)