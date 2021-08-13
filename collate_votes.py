import json
import csv
import argparse


tag_map = {'B-PER':0, 'I-PER':1, 'B-LOC':2, 'I-LOC':3, 'B-ORG':4, 'I-ORG':5, 'B-MISC':6, 'I-MISC':7, 'O':8}
tag_id_map = inv_map = {v: k for k, v in tag_map.items()}
lang_map = {'Hindi':'hin', 'Bengali':'ben', 'Marathi':'mar', 'Tamil':'tam'}

def collate():
    with open(args.votes_file, encoding='utf-8') as f:
        data = json.load(f)

    for (lang,id) in lang_map.items():
        header = ["sent_id", "word", "assigned_tag", "max_voted_tags"]
        lang_data = [each for each in data if each.get('lang', '') == id]
        count = match_tags = mismatch_tags = multiple_tags = 0
        if lang_data:
            f = open(id + "_" + args.out_corpus_file, 'w')
            of = open(id + "_" + args.out_votes_file, 'w', newline='\n')
            csv_writer = csv.writer(of, delimiter=',')
            count = 1
            for sent in lang_data:
                if "relevence" in sent.keys() and sent["relevence"] <= 0:
                    continue
                if count == 1:
                    csv_writer.writerow(header)
                line = [count]
                for entry in sent["words"]:
                    m = max(entry["votes"])
                    voted_tags = [tag_id_map[i] for i, j in enumerate(entry["votes"]) if j == m]
                    og_tag = tag_id_map[entry["tag"]]
                    line.extend([entry["word"], og_tag])
                    line.extend(voted_tags)
                    if len(voted_tags) == 1:
                        if og_tag == voted_tags[0]:
                            match_tags +=1
                            line.append("")
                        else:
                            mismatch_tags +=1
                            line.append("*")
                        f.write(entry["word"] + " " + voted_tags[0] + "\n")
                    else:
                        multiple_tags +=1
                        f.write(entry["word"] + " " + " ".join(voted_tags) + "\n")
                    csv_writer.writerow(line)
                    line = [""]
                count += 1
                f.write("\n")    
            of.close()
            f.close()
        print(f"\n{lang}")
        print(f"#matching tags: {match_tags}\t#mismatch tags: {mismatch_tags}\t#words with >1 voted tag: {multiple_tags}")
        print(f"#sentences chosen: {count}")
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Creates a refined corpus based on voted tags")
    parser.add_argument("--votes_file", type=str, required=True)
    parser.add_argument("--out_votes_file", type=str, default="votes.txt")
    parser.add_argument("--out_corpus_file", type=str, default="cleaned.txt")
    args = parser.parse_args()
    collate()