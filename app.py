from flask import Flask, render_template, redirect, request, flash, session
from pymongo import MongoClient
import random
import json
from bson import json_util


# config system
app = Flask(__name__)
app.config.update(dict(SECRET_KEY='yoursecretkey'))
client = MongoClient('localhost:27017')
db = client.ner_corpus
num_sents_display = 5
tag_id_map = {0:'B-PER', 1:'I-PER', 2:'B-LOC', 3:'I-LOC', 4:'B-ORG', 5:'I-ORG', 6:'B-MISC', 7:'I-MISC', 8:'O'}

def fetch_data(lang):
    docs = db.sentences.find({'lang':lang})
    docs = json.loads(json_util.dumps(docs))
    data = []
    for i in docs:
        data.append(i)
    # print(data)
    data = sorted(data, key=lambda item: item['vote'])[:num_sents_display]
    random.shuffle(data)
    return data
  

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
                { "$inc": { "vote": 1, "relevance": user_score} }
            )
        db.sentences.update_one(
                {"ID": id},
                { "$set": { f"words.{i}.votes": upd_votes} }
            )
    next = True if 'next' in request.form.keys() else False
    if next:
        session['curr_it'] += 1
        print(f"Sentence: {session['curr_it']+1}/{session['num_it']}")
        if session['curr_it'] < session['num_it']:
            flash(f"Sentence: {session['curr_it']+1}/{session['num_it']}", "warning")
            return redirect(f"/update/{session['data'][session['curr_it']]['ID']}")
        else:
            flash("You have successfully finished annotating!", "success")
            return redirect("/")
    else:
        flash("Your previous session ended! All annotations were saved.", "success")
        return redirect("/")

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        lang = request.form['lang']
        session['data'] = fetch_data(lang)
        session['num_it'] = len(session['data'])
        session['curr_it'] = 0
        if session['num_it']:
            print(f"Sentence: {session['curr_it']+1}/{session['num_it']}")
            return redirect(f"/update/{session['data'][session['curr_it']]['ID']}")
        else:
            flash(f"No sentences available for selected language: {lang}!", "danger")
            return render_template('home.html')
    return render_template('home.html')


if __name__== '__main__':
    app.run(debug=True)
