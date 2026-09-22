import json 

def save_json(products,path):
    with open(path,"w",encoding="utf-8") as file:
            json.dump(products,file,ensure_ascii=False,indent=4)

