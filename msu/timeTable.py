import json
timetable={
    "Пн": {"тип":1, "время":"19:30",'опрос':["21:00", "23:00"], 'дистанция':7,'темп':"7:00", "отмена":0, "оповещение":"10:00"},
    "Вт": {"тип":2, "время":"19:30",'опрос':["21:00", "23:00"], "отмена":0,"оповещение":"10:00"},
    "Ср": {"тип":1, "время":"19:30",'опрос':["21:00", "23:00"],'дистанция':10,'темп':"7:00", "отмена":0, "оповещение":"10:00"},
    "Чт": {"тип":2, "время":"19:30",'опрос':["21:00", "23:00"],  "отмена":0,  "оповещение":"10:00"},
    "Пт": {"тип":0, "оповещение":"10:00"},
    "Сб": {"тип":0, "оповещение":"10:00"},
    "Вс": {"тип":1, "время":"17:00",'опрос':["12:00", "14:00"], 'дистанция':10,'темп':"6:30", "отмена":0, "оповещение":"09:00"}
}
phrasses={
    'no_train': ['Сегодня нет тренировок &#128164;',
             'Сегодня нет тренировок &#128564;',
             'Сегодня нет занятии, отдыхаем &#128526;'],
    'cancel_tomorrow':
        ['Завтра тренировки не будет..',
         'На завтра отменили тренировку &#128560;'],
    'longrun_tomorrow':
        ['Уже завтра лонгран &#127939;{ на dist км[ с темпом temp мин/км]}, time, сбор возле входа ГЗ со стороны Ломоносова. Всех ждём!',
        'Завтра в time пройдет лонгран{ на dist км[ с темпом temp мин/км]}. Ждем всех у главного входа Гз &#128522;'],
    'workout_tomorrow':
        ['Уже завтра функциональная тренировка &#127947;, time, сбор возле входа ГЗ со стороны Ломоносова. Всех ждём!',
        'Завтра в time пройдет функциональная тренировка &#128170;. Ждем всех у главного входа Гз &#128522;'],
    'cancel_today':
        ['Сегодня тренировки не будет(',
         'Ошибочка, сегодня тренировку отменили &#128547;',
         'Сегодня отменили тренировку &#128560;'],
    'longrun_today':
        ['Уже сегодня лонгран{ на dist км[ с темпом temp мин/км]} &#127939;, time, сбор возле входа ГЗ со стороны Ломоносова. Всех ждём!',
        'Сегодня в time пройдет лонгран{ на dist км[ с темпом temp мин/км]}. Ждем всех у главного входа Гз &#128522;'],
    'workout_today':
        ['Уже сегодня функциональная тренировка &#127947;, time, сбор возле входа ГЗ со стороны Ломоносова. Всех ждём!',
        'Сегодня в time пройдет функциональная тренировка &#128170;. Ждем всех у главного входа Гз &#128522;']
             }
def write(data,filename):
    data=json.dumps(data)
    data=json.loads(str(data))
    with open(filename,'w',encoding='utf-8') as file:
        json.dump(data,file)
def read(filename):
    with open(filename,'r',encoding='utf-8') as file:
        return json.load(file)
def restart_timetable():
    return timetable
def restart_phrasses():
    return phrasses
def convertTime(_time):
    res=str(_time['часы'])+":"+str(_time['минуты'])
    if(_time['часы']<10):
        res="0"+res
    if(_time['минуты']<10):
        res=res[:3]+'0'+res[3]
    return res
def shiftTime(t):
    hour=int(t[:2])-3
    if(hour<0):
        hour+=24
    if(hour<10):
        return '0'+str(hour)+t[2:]
    return str(hour)+t[2:]


def checkTime(time):
    if(len(time)==5):
        if(time[:2].isdigit() and time[2]==':' and time[3:].isdigit()
           and int(time[:2])<24 and int(time[3:])<60):
            return 1#правильный формат
        return -1#неверный формат
    if(len(time)==3):
        if(time[0].isdigit() and time[1]==':' and time[2].isdigit()):
            return 0 #нужно исправить
        return -1#неверный формат
    if(len(time)==4):
        if(time[0].isdigit() and time[1]==':' and time[2:].isdigit()
           and int(time[2:])<60):
            return 0 #нужно исправить
        if(time[:2].isdigit() and time[2]==':' and time[3].isdigit()
           and int(time[:2])<24):
            return 0 #нужно исправить
        return -1
    return -1
def fixedTime(time):
    if(len(time)==3):
        return '0'+time[:2]+'0'+time[2]
    if(time[1]==':'):
        return '0'+time
    return time[:3]+'0'+time[3]

def getPhrassesForDelete(name):
    phrasses=read("phrasses")
    text="Список фраз на теманику "+name+"\n"
    for i, phrase in enumerate(phrasses[name]):
        text+=str(i)+"\t"+phrase+"\n"
    return text


1