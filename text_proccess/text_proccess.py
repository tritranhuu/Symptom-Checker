# from co
# nfigs import data_file
from configs import data_file

class TextProcess():
    def __init__(self, lang="vi"):
        self.whitelist = '0123456789abcdđefghijklmnopqrstuvwxyzàáảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệoòóỏõọôồốổỗộơờớởỡợuùúủũụưừứửữựiìíỉĩịyỳýỷỹỵ '
        self.lang = lang
        if lang == "vi":
            stopwords = open(data_file.APP_STOPWORD_DICT_VI, "r")
            self.stopwords = stopwords.readlines()
            symptom_dict = open(data_file.APP_SYMPTOM_DICT_VI, "r")
            self.symptom_dict = [s.strip() for s in symptom_dict.readlines()]
        elif lang == "en":
            stopwords = open(data_file.APP_STOPWORD_DICT_EN, "r")
            self.stopwords = stopwords.readlines()
            symptom_dict = open(data_file.APP_SYMPTOM_DICT_EN, "r")
            self.symptom_dict = [s.strip() for s in symptom_dict.readlines()]
            
    def set_lang(self, lang):
        if lang == self.lang:
            return 1
        elif lang == "vi":
            stopwords = open(data_file.APP_STOPWORD_DICT_VI, "r")
            self.stopwords = stopwords.readlines()
            symptom_dict = open(data_file.APP_SYMPTOM_DICT_VI, "r")
            self.symptom_dict = [s.strip() for s in symptom_dict.readlines()]
            return 1
        elif lang == "en":
            stopwords = open(data_file.APP_STOPWORD_DICT_EN, "r")
            self.stopwords = stopwords.readlines()
            symptom_dict = open(data_file.APP_SYMPTOM_DICT_EN, "r")
            self.symptom_dict = [s.strip() for s in symptom_dict.readlines()]
            return 1
        else:
            return 0

    def filter_line(self, line):
        return ''.join([ch for ch in line if ch in self.whitelist])
    
    def remove_stop_words(self, sentence):
        sentence = sentence.replace(",", " ")
        slist = sentence.split()
        ret = ""
        for item in slist:
            if item not in self.stopwords and len(item)>0:
                ret = ret + " " + item
        ret = ret.strip()
        return ret

    def extract(self, sentence):
        sentence = sentence.lower()
        sentence = self.filter_line(sentence)
        sentence = self.remove_stop_words(sentence)
        sentence = sentence.split()
        symptoms = []
        remainder = sentence
        if self.lang == "vi":
            offset = 5
        elif self.lang == "en":
            offset = 4
        while len(remainder) > 0:
            gotcha = 0
            for e in range(offset,0,-1):
                word = '_'.join(remainder[0:e])
                print(word)
                if word in self.symptom_dict:
                    symptoms.append(word)
                    remainder = remainder[e:]
                    gotcha = 1
                    break
            if gotcha == 1:
                continue
            remainder = remainder[1:]
        return symptoms

if __name__ == "__main__":
    text_process = TextProcess()
    sent = "Đau bụng, ỉa chảy"
    # sent = sent.lower()
    # sent = text_process.remove_not_meaning_words(sent)
    # sent = text_process.remove_stop_words(sent)
    print(text_process.extract(sent))
    print(sent)