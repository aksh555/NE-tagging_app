from flask import Flask, render_template, redirect, request
from pymongo import MongoClient


# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('localhost:27017')
db = client.ner_corpus

class utils:
    def __init__(self):
        self.it = 0
        self.type = "start"
        self.data = []
        self.num_sents_display = 2
    def get_data(self, lang):
        print(lang)
        docs = db.sentences.find({'lang':lang})
        for i in docs:
            self.data.append(i)
        print(len(self.data))
        self.data = sorted(self.data, key=lambda item: item['vote'])[:self.num_sents_display]
        # print(self.data)
        self.it = 0
    def increment(self):
        while self.it < len(self.data) - 1:
            self.it += 1
            i = self.data[self.it]
            return i
        return None

util = utils()

tag_id_map = {0:'B-PER', 1:'I-PER', 2:'B-LOC', 3:'I-LOC', 4:'B-ORG', 5:'I-ORG', 6:'B-MISC', 7:'I-MISC', 8:'O'}
    

@app.route("/update/<int:id>", methods=['GET'])
def updateLabel(id):
    sent = db.sentences.find_one({'ID':id})
    id = sent['ID']
    words = sent['words']
    return render_template('edit.html', id=id, words=words, tag_id_map=tag_id_map)


@app.route('/update', methods=['POST'])
def update():
    id = int(request.form['id'])
    sent = db.sentences.find_one({'ID':id})
    user_score = int(request.form['score'])
    for i in range(len(sent['words'])):
        upd_votes = sent['words'][i]['votes']
        choice = int(request.form[f"choice{i}"])
        upd_votes[choice] += 1  
        if i==0:
            db.sentences.update_one(
                {"ID": id},
                { "$inc": { "vote": 1, "relevence": user_score} }
            )
        db.sentences.update_one(
                {"ID": id},
                { "$set": { f"words.{i}.votes": upd_votes} }
            )
    
    if util.increment():
        return redirect(f"/update/{util.data[util.it]['ID']}")
    util.data = []
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        lang = request.form['lang']
        util.get_data(lang)
        if util.data:
            return redirect(f"/update/{util.data[0]['ID']}")
        else:
            return render_template('home.html', back=lang)
    return render_template('home.html', back="")


if __name__== '__main__':
    app.run(debug=True)
