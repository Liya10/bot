import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
#from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton

#from timeTable import write, read, restart, help, convertTime, shiftTime, checkTime, fixedTime
from timeTable import write, read, fixedTime,  shiftTime, checkTime
from timeTable import restart_timetable, restart_phrasses, getPhrassesForDelete


from generateKeyboard import ADMIN,SUPER,NORM,BAD,ABSENT, CHANGE,ADD,DELETE,SHOW_DAY,WORKOUT,LONG
from generateKeyboard import CANCEL,YES,NO, TODAY, TOMORROW
from generateKeyboard import START_THE_COUNT,STOP_THE_COUNT,SHOW,EXIT,MONDAY
from generateKeyboard import HOUR_8,HOUR_19
from generateKeyboard import MIN_0,MIN_55, NO_DIST, DIST_3, DIST_40
from generateKeyboard import NO_TEMP, TEMP_4, TEMP_5, TEMP_6, TEMP_7
from generateKeyboard import SURVEY, SHOW_SURVEY
from generateKeyboard import NOTIFY, NOTIFY_TIME, NOTIFY_GET, NOTIFY_CHANGE


from generateKeyboard import get_keyboard_for_admin, get_keyboard_cancel, get_keyboard_day
from generateKeyboard import get_keyboard_add, get_keyboard_hour, get_keyboard_minute
from generateKeyboard import get_keyboard_change, get_keyboard_type, get_keyboard_confirmation
from generateKeyboard import get_keyboard_delete, get_keyboard_dist, get_keyboard_temp
from generateKeyboard import get_keyboard_cancel_confirmation, get_keyboard_survey
from generateKeyboard import get_keyboard_survey_info, get_keyboard_notify_change
from generateKeyboard import get_keyboard_notify,get_keyboard_notify_time
from generateKeyboard import get_keyboard_notify_time_change, get_keyboard_vote

import datetime
import schedule
from threading import Thread
import time
from random import choice

import json
import pandas as pd
import numpy as np



NumConvertToDay={0:'Пн', 1:'Вт', 2:'Ср', 3:'Чт', 4:'Пт', 5:'Сб', 6:'Вс'}
NumConvertToDay2={0:'в понедельник', 1:'во вторник', 2:'в среду',
3:'в четверг', 4:'в пятницу', 5:'в субботу', 6:'в воскресенье'}
DayConvertToNum={'Пн':0,'Вт':1 ,'Ср':2 ,'Чт':3 ,'Пт':4 , 'Сб':5, 'Вс':6,
                'пн':0,'вт':1 ,'ср':2 ,'чт':3 ,'пт':4 , 'сб':5, 'вс':6}
typeWorkout={'лонгран':1, 'функциональная тренировка':2, 'функциональная':2,'тренировка':2, 'отмена':0}
CorrectConvert={'пн':'Пн','понедельник':'Пн',
                'вт':'Вт','вторник':'Вт',
                'ср':'Ср','среда':'Ср',
                'чт':'Чт','четверг':'Чт',
                'пт':'Пт','пятница':'Пт',
                'сб':'Сб','суббота':'Сб',
                'вс':'Вс','воскресенье':'Вс'
               }

class MyBotLongPoll(VkBotLongPoll):
    def listen(self):
        while(True):
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print(e)


class Bot:

    timetable=read('timetable')
    survey=pd.read_csv('survey.csv',  sep = ',', index_col=['survey_id', 'user_id'])
    if(datetime.datetime.now().hour>20):
        dayOnWeek=(datetime.datetime.now().weekday()+1)%7
    else:
        dayOnWeek=datetime.datetime.now().weekday()
    stopThread=False
    changeSchedule=True
    wait_time=False
    minute=datetime.datetime.now().minute
    survey_on=False

    delete_phrase="0"
    add_phrase="0"
    def __init__(self, tok, _id, chat_id):

        self.chat_id=chat_id
        self.peer_id=2000000000+chat_id

        self.vk_session=vk_api.VkApi(token=tok)
        self.longpoll=MyBotLongPoll(self.vk_session, _id)
        self.buf_admin=[elem['member_id'] for elem in self.vk_session.method("messages.getConversationMembers",
                        {"peer_id":self.peer_id,"fields":'items'}) ['items']
                        if (elem.get('is_admin',False) and elem['is_admin'] is True and elem['member_id']>0)]

    def __call__(self):
        thread = Thread(target=self.do_schedule)
        thread.start()

        for event in self.longpoll.listen():
            if(event.type==VkBotEventType.MESSAGE_NEW and
                event.object.message['from_id'] in self.buf_admin and event.from_user):
                _id=event.object.message['from_id']
                if('payload' in event.object.message):

                    payload=event.object.message['payload'][1:-1].split(',')

                    #сигналы от клавиатуры админа
                    if(int(payload[0])==CHANGE):#сигнал изменения расписания
                        #нужно послать клавиатуру о выборе дня недели
                        post=self.getPost(_id, "Хм, какой день недели Вас интересует?")
                        post['keyboard']= get_keyboard_day().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==CANCEL)&(len(payload)==1)):#сигнал об отмене тренировки #ok
                        #нужно уточнить отмена на ближайщую тренировку или на определенный день недели
                        text="Вы желаете отменить ближайщую тренировку или за определенный день?"
                        post=self.getPost(_id,text)
                        post['keyboard']= get_keyboard_cancel().get_keyboard()
                        self.sender(post)

                    elif(int(payload[0])==SHOW):#сигнал о предоставлении расписании тренировок
                        post=self.getPost(_id, self.printTimeTable())
                        self.sender(post)#передаем расписание в личку
                        post=self.getPost(_id, "Что-то еще?&#128064;")
                        post['keyboard']=get_keyboard_for_admin().get_keyboard()
                        self.sender(post)#возвращаем клавиатуру
                    elif(int(payload[0])==EXIT):#сигнал выхода
                        #нужно попращаться и убрать клавиатуру
                        post=self.getPost(_id, "Пока &#128075;")
                        post['keyboard']=get_keyboard_for_admin().get_empty_keyboard()
                        self.sender(post)

                    #сигнал от клавиатуры отмены тренировки
                    #на определенный день недели
                    elif((int(payload[0])==CANCEL)&(len(payload)==2)):
                        day=int(payload[1])-MONDAY
                        if(day==-1):
                            day=self.getNextWorkout()
                        if(self.timetable[NumConvertToDay[day]]['тип']==0):
                            text="Хм, в этот день не проводят ни каких тренировок.\nМогу ли чем-нибудь другим помочь?"
                            post=self.getPost(_id, text)
                            post['keyboard']=get_keyboard_for_admin().get_keyboard()
                            self.sender(post)
                        else:
                            if(self.timetable[NumConvertToDay[day]]['отмена']==1):
                                text="Тренировку "+NumConvertToDay2[day]+" уже отменили.\nМогу ли чем-нибудь другим помочь?"
                                post=self.getPost(_id, text)
                                post['keyboard']=get_keyboard_for_admin().get_keyboard()
                                self.sender(post)
                            else:
                                text="По записям тренировку "+NumConvertToDay2[day]+" еще не отменили.\n"
                                if(self.timetable[NumConvertToDay[day]]['тип']==1):
                                    text+="В этот день "+self.timetable[NumConvertToDay[day]]['время']+" проходит лонгран"
                                    if('дистанция' in self.timetable[NumConvertToDay[day]]):
                                        text+=" на "+str(self.timetable[NumConvertToDay[day]]['дистанция'])+" км"
                                        if('темп' in self.timetable[NumConvertToDay[day]]):
                                            text+=" с темпом "+str(self.timetable[NumConvertToDay[day]]['темп'])+" мин/км"
                                else:
                                    text+="В этот день "+self.timetable[NumConvertToDay[day]]['время']+" проходит функциональная тренировка"
                                text+=".\nВы точно желаете отменить тренировку?"
                                post=self.getPost(_id, text)
                                post['keyboard']=get_keyboard_cancel_confirmation(day).get_keyboard()
                                self.sender(post)
                    elif((int(payload[0])==CANCEL)&(len(payload)==3)):
                        day=int(payload[1])
                        self.timetable[NumConvertToDay[day]]['отмена']=1
                        write(self.timetable,'timetable')
                        text="Хорошо, мы оповестим об отмене &#128522;\nЧто-то еще?&#128064;"
                        post=self.getPost(_id, text)
                        post['keyboard']=get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    #сигнал от клавиатуры об изменении расписания
                    #нужно определить день недели
                    elif((int(payload[0])>=MONDAY)&(int(payload[0])<=MONDAY+6)):#выбрали день недели
                        day=int(payload[0])-MONDAY
                        day_str=NumConvertToDay[day]
                        #тут два варианта:1)если есть тренировка, но можем ее изменить или удалить; 2)если нет тренировки, то добавить
                        if(self.timetable[day_str]['тип']>0):#если есть тренировка
                            #клавиатура с кнопка: удалить, изменить, показать и ничего не делать
                            text="В этом дне проходит "
                            if(self.timetable[day_str]['тип']==2):
                                text+="функциональная тренировка.\nВы желаете ..."
                            else:
                                text+="лонгран"
                                if('дистанция' in self.timetable[day_str]):
                                    text+=" на "+str(self.timetable[day_str]['дистанция'])+" км"
                                    if('темп' in self.timetable[day_str]):
                                        text+=" с темпом "+str(self.timetable[day_str]['темп'])+" мин/км.\nВы желаете ..."
                                    else:
                                        text+=".\nВы желаете ..."
                                else:
                                    text+=".\nВы желаете ..."
                            post=self.getPost(_id, text)
                            post['keyboard']=get_keyboard_change(day).get_keyboard()
                            self.sender(post)
                        else:#если нет
                            #клавиатура с кнопка: добавить и ничего не делать
                            post=self.getPost(_id, "В этом дне нет тренировок.\nХотите добавить?")
                            post['keyboard']=get_keyboard_add(day).get_keyboard()
                            self.sender(post)
                    #сигнал о добавлении тренировки
                    elif(int(payload[0])==ADD):
                        #нужно уточнить время
                        post=self.getPost(_id, "Хорошо, выберите часы:")
                        post['keyboard']=get_keyboard_hour(int(payload[1])).get_keyboard()
                        self.sender(post)
                    #нужно определить часы
                    elif((int(payload[0])>=HOUR_8)&(int(payload[0])<=HOUR_19)):
                        #нужно уточнить минуты
                        post=self.getPost(_id, "Выберите минуты:")
                        post['keyboard']=get_keyboard_minute(int(payload[1]),int(payload[0])-HOUR_8+8 ).get_keyboard()
                        self.sender(post)
                    #нужно определить минуты
                    elif((int(payload[0])>=MIN_0)&(int(payload[0])<=MIN_55)):
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[0])-MIN_0
                        #нужно уточнить тип тренировки
                        post=self.getPost(_id, "Выберите тип тренировки:")
                        post['keyboard']=get_keyboard_type(day,hour,minute).get_keyboard()
                        self.sender(post)
                    #нужно определить тип
                    elif((int(payload[0])==WORKOUT)):
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[3])
                        time=str(hour)+":"+str(minute)
                        if(checkTime(time)==0):
                            time=fixedTime(time)
                        text="Отлично. Значит "+NumConvertToDay2[day]+" "+time+" пройдет функциональная тренировка."
                        text+="\nПодтверждаете изменения?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_confirmation(day,hour, minute,int(payload[0])).get_keyboard()
                        self.sender(post)
                    #нужно определить тип
                    elif(int(payload[0])==LONG):
                        #нужно подтвердить измененияget_keyboard_confirmation(day,hour,minute,typeWorkout)
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[3])
                        text='Не хотите указать приблизительную дистанцию?'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_dist(day,hour, minute,int(payload[0])).get_keyboard()
                        self.sender(post)
                    #нужно определить тип
                    elif(int(payload[0])==NO_DIST):
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[3])
                        typeWorkout=int(payload[4])
                        time=str(hour)+":"+str(minute)
                        if(checkTime(time)==0):
                            time=fixedTime(time)
                        text="Отлично. Значит "+NumConvertToDay2[day]+" "+time+" пройдет лонгран."
                        text+="\nПодтверждаете изменения?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_confirmation(day,hour, minute,typeWorkout).get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])>=DIST_3)&(int(payload[0])<=DIST_40)):
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[3])
                        typeWorkout=int(payload[4])
                        dist=int(payload[0])-NO_DIST
                        text="Хорошо, так и запишем &#9997;\nЛонгран на "+str(dist)+" км."
                        text+="\nНе хотите указать темп?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_temp(day,hour, minute,typeWorkout, dist).get_keyboard()
                        self.sender(post)
                    #сигнал о подтверждении изменении
                    elif((int(payload[0])>=NO_TEMP)&(int(payload[0])<=TEMP_7)):
                        day=int(payload[1])
                        hour=int(payload[2])
                        minute=int(payload[3])
                        typeWorkout=int(payload[4])
                        dist=int(payload[5])
                        temp=int(payload[0])
                        time=str(hour)+":"+str(minute)
                        if(checkTime(time)==0):
                            time=fixedTime(time)
                        text="Отлично. Значит "+NumConvertToDay2[day]+" "+time+" пройдет лонгран на "+str(dist)+" км"
                        if(temp==NO_TEMP):
                            text+='.'
                        elif((temp>=TEMP_4)&(temp<TEMP_5)):
                            text+=" с темпом 4:"+str(temp-TEMP_4)+" мин/км."
                        elif((temp>=TEMP_5)&(temp<TEMP_6)):
                            text+=" с темпом 5:"+str(temp-TEMP_5)+" мин/км."
                        elif((temp>=TEMP_6)&(temp<TEMP_7)):
                            text+=" с темпом 6:"+str(temp-TEMP_6)+" мин/км."
                        else:
                            text+=" с темпом 7:00 мин/км."
                        text+="\nПодтверждаете изменения?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_confirmation(day,hour, minute,typeWorkout, dist, temp).get_keyboard()
                        self.sender(post)
                    elif(int(payload[0])==YES):
                        day=int(payload[1])
                        day_str=NumConvertToDay[day]
                        hour=payload[2]
                        sur_hour1=int(hour)+2
                        if(sur_hour1>=24):
                            sur_hour1-=24
                        sur_hour2=sur_hour1+2
                        if(sur_hour2>=24):
                            sur_hour2-=24
                        survey_time=[fixedTime(str(sur_hour1)+":00"), fixedTime(str(sur_hour2)+":00")]
                        minute=payload[3]
                        typeWorkout=int(payload[4])
                        dist=int(payload[5])
                        temp=payload[6]
                        time=hour+":"+minute
                        if(checkTime(time)==0):
                            time=fixedTime(hour+":"+minute)
                        tmp=self.timetable[day_str]['оповещение']
                        if(typeWorkout==WORKOUT):

                            self.timetable[day_str]={'тип':2, 'время':time,"опрос":survey_time, "отмена":0, 'оповещение': tmp}
                        elif(typeWorkout==LONG):
                            if(dist>0):
                                if(int(temp)>NO_TEMP):
                                    self.timetable[day_str]={'тип':1, 'время':time,"опрос":survey_time, 'дистанция':dist,'темп':temp[0]+":"+temp[1:],"отмена":0, 'оповещение': tmp}
                                else:
                                    self.timetable[day_str]={'тип':1, 'время':time,"опрос":survey_time, 'дистанция':dist,"отмена":0, 'оповещение': tmp}
                            else:
                                self.timetable[day_str]={'тип':1, 'время':time,"опрос":survey_time,"отмена":0, 'оповещение': tmp}
                        write(self.timetable,'timetable')
                        post=self.getPost(self.chat_id, "Расписание изменилось! &#9881;", True)
                        self.sender(post)
                        post=self.getPost(_id, "Хорошо, я оповестил об изменении в расписании &#128522;\nЧто-то еще?&#128064;")
                        post['keyboard']=  get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    #отказ о подтверждении изменении
                    elif(int(payload[0])==NO):
                        post=self.getPost(_id, "Ладно, я сбросил измения &#128517;\nЧто-то еще?&#128064;")
                        post['keyboard']=  get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    #удалить тренировку
                    elif((int(payload[0])==DELETE)&(len(payload)==2)):
                        post=self.getPost(_id, "Вы уверены, что хотите удалить тренировку?")
                        post['keyboard']= get_keyboard_delete(int(payload[1])).get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==DELETE)&(len(payload)==3)):
                        if(int(payload[1])==YES):
                            day=NumConvertToDay[int(payload[2])]
                            time=self.timetable[day]["оповещение"]
                            self.timetable[day]={'тип': 0, "оповещение":time}
                            write(self.timetable,'timetable')
                            post=self.getPost(self.chat_id, "Расписание изменилось! &#9881;", True)
                            self.sender(post)
                            post=self.getPost(_id, "Тренировка была успешно удалена\nЧто-то еще?&#128064;")
                        else:
                             post=self.getPost(_id, "Ладно, я сбросил изменения &#128517;\nЧто-то еще?&#128064;")
                        post['keyboard']= get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    #возвращение исходной клавы
                    elif(int(payload[0])==ADMIN):#сигнал о возращение исходной клавиатуры
                        text="Ладно &#128517;\nЧто-то еще? &#128064;"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    #показать расписание
                    elif(int(payload[0])==SHOW_DAY):#сигнал показать расписание на определенный день
                        day=int(payload[1])
                        day_str=NumConvertToDay[day]
                        time=self.timetable[day_str]['время']
                        canceled=self.timetable[day_str]['отмена']
                        text=day_str+" в "+time+" "
                        if(self.timetable[day_str]['тип']==1):
                            text+='будет лонгран'
                        else:
                            text+='идет функциональная тренировка'
                        if(canceled==1):
                            text+=', но тренировку отменили'
                        post=self.getPost(_id, text)
                        self.sender(post)
                        post=self.getPost(_id, "Что-то еще?")
                        post['keyboard']= get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==SURVEY)&(len(payload)==1)):
                        #Если опрос включен
                        if(self.survey_on):
                            text='Вы хотите отключить или что-то узнать?'
                        else:
                            text='Вы хотите включить или что-то узнать?'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_survey(self.survey_on).get_keyboard()
                        self.sender(post)
                    elif(int(payload[0])==START_THE_COUNT):
                        self.survey_on=True
                        text='Хорошо, опрос включен, начнется после тренировки &#128522;\nЧто-то еще?&#128064;'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_survey(True).get_keyboard()
                        self.sender(post)
                    elif(int(payload[0])==STOP_THE_COUNT):
                        self.survey_on=False
                        text='Хорошо, опрос выключен\nЧто-то еще?&#128064;'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_survey(False).get_keyboard()
                        self.sender(post)
                    elif(int(payload[0])==SHOW_SURVEY):
                        text='Вам интересны результаты за определенный день или в целом?'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_survey_info().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==SURVEY)&(len(payload)==2)):
                        day= int(payload[1])-MONDAY
                        if(day==-1):
                            #нужно отправить результаты за всю неделю
                            survey=pd.read_csv('survey.csv',  sep = ',', index_col=['survey_id', 'user_id'])
                            tmp=survey['result_last']
                            text="Результаты за весь период\n\n"
                            text+="Super    "+str(np.sum(tmp==SUPER))+"\n"
                            text+="Norm     "+str(np.sum(tmp==NORM))+"\n"
                            text+="Bad      "+str(np.sum(tmp==BAD))+"\n"
                            text+="Absent   "+str(np.sum(tmp==ABSENT))+"\n"
                            text+='\nЧто-то еще?'
                            post=self.getPost(_id, text)
                            post['keyboard']= get_keyboard_survey(self.survey_on).get_keyboard()
                            self.sender(post)

                        else:
                            #за определенный день
                            #нужно отправить результаты за всю неделю
                            survey=pd.read_csv('survey.csv',  sep = ',', index_col=['survey_id', 'user_id'])
                            survey=survey[survey.day==day]
                            tmp=survey['result_last']
                            text="Результаты за"+NumConvertToDay[day]+"период\n\n"
                            text+="Super    "+str(np.sum(tmp==SUPER))+"\n"
                            text+="Norm     "+str(np.sum(tmp==NORM))+"\n"
                            text+="Bad      "+str(np.sum(tmp==BAD))+"\n"
                            text+="Absent   "+str(np.sum(tmp==ABSENT))+"\n"
                            text+='\nЧто-то еще?'
                            post=self.getPost(_id, text)
                            post['keyboard']= get_keyboard_survey(self.survey_on).get_keyboard()
                            self.sender(post)

                    elif(int(payload[0])==NOTIFY):
                        text='Класс.'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_TIME)& (len(payload)==1)):
                        text=self.getNotifyTime()
                        text+='Выберите день недели'
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify_time().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_TIME)& (len(payload)==2)):
                        day=int(payload[1])-MONDAY
                        text='Хорошо, выберите время оповещения для '+NumConvertToDay[day]
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify_time_change(day).get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_TIME)& (len(payload)==3)):
                        day=NumConvertToDay[int(payload[1])]
                        time=fixedTime(payload[2]+":00")
                        self.timetable[day]['оповещение']=time
                        text='Хорошо, мы изменили время оповещения.\nТеперь\n'
                        text+=self.getNotifyTime()
                        text+="\nЧто-то еще с оповещением?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify().get_keyboard()
                        self.sender(post)
                    elif(int(payload[0])==NOTIFY_GET):
                        phrasses=read("phrasses")
                        text="Набор фраз оповещения:\n"
                        for name in phrasses:
                            text+=name+"\n"
                            for i, phrase in enumerate(phrasses[name]):
                                text+=str(i)+"\t"+phrase+"\n"
                            text+="\n"
                        text+="Хотите ли изменить оповещение?"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_CHANGE)&(len(payload)==1)):
                        text="Вы хотите удалить или добавить?\n"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify_change().get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_CHANGE)&(len(payload)==2)):
                        #нет разницы между add и delete
                        text="Выберите тему оповещения\n"
                        post=self.getPost(_id, text)
                        post['keyboard']= get_keyboard_notify_change(int(payload[1])).get_keyboard()
                        self.sender(post)
                    elif((int(payload[0])==NOTIFY_CHANGE) &(len(payload)>2)):
                        if(int(payload[1])==DELETE):
                            if(int(payload[2])==WORKOUT):
                                if(int(payload[2])==TODAY):
                                    self.delete_phrase="workout_today"
                                    text=self.getPhrassesForDelete("workout_today")
                                elif(int(payload[2])==TOMORROW):
                                    self.delete_phrase="workout_tomorrow"
                                    text=getPhrassesForDelete("workout_tomorrow")
                                else:
                                    self.delete_phrase="no_train"
                                    text=getPhrassesForDelete("no_train")
                            elif(int(payload[1])==LONG):
                                if(int(payload[2])==TODAY):
                                    self.delete_phrase="longrun_today"
                                    text=getPhrassesForDelete("longrun_today")
                                elif(int(payload[2])==TOMORROW):
                                    self.delete_phrase="longrun_tomorrow"
                                    text=getPhrassesForDelete("longrun_tomorrow")
                            elif(int(payload[1])==CANCEL):
                                if(int(payload[2])==TODAY):
                                    self.delete_phrase="workout_today"
                                    text=getPhrassesForDelete("workout_today")
                                elif(int(payload[2])==TOMORROW):
                                    self.delete_phrase="workout_tomorrow"
                                    text=getPhrassesForDelete("workout_tomorrow")
                            print("Введите индекс:")
                            text+="Введите индекс:"
                            post['keyboard']= get_keyboard_notify_change().get_empty_keyboard()
                            self.sender(post)
                        elif(int(payload[1])==ADD):
                            if(int(payload[2])==WORKOUT):
                                if(int(payload[2])==TODAY):
                                    self.add_phrase="workout_today"
                                    text=getPhrassesForDelete("workout_today")
                                    text+="Введите фразу, маскирируя время как time "
                                elif(int(payload[2])==TOMORROW):
                                    self.add_phrase="workout_tomorrow"
                                    text=getPhrassesForDelete("workout_tomorrow")
                                    text+="Введите фразу, маскирируя время как time "
                                else:
                                    self.add_phrase="no_train"
                                    text=getPhrassesForDelete("no_train")
                                    text+="Введите фразу... "
                            elif(int(payload[1])==LONG):
                                if(int(payload[2])==TODAY):
                                    self.add_phrase="longrun_today"
                                    text=getPhrassesForDelete("longrun_today")
                                elif(int(payload[2])==TOMORROW):
                                    self.add_phrase="longrun_tomorrow"
                                    text=getPhrassesForDelete("longrun_tomorrow")
                                text+="Введите фразу, маскирируя время как time"
                                text+=",но если в тексте есть дистанция, то замаскируйте ее как dist, "
                                text+="а также начала и конец брать за {...dist км...}\n"
                                text+="Если еще и темп хотите добавить, то сделайте метку temp"
                                text+=", а содержимое вложите [...temp мин/км...]\n"
                                text+="Учтите, что темп должен быть вложен в дистацию, то есть "
                                text+=" ... {... dist км ...[... temp мин/км... ]...}...\n"
                                text+="Иначе выдаст ошибку"
                            elif(int(payload[1])==CANCEL):
                                if(int(payload[2])==TODAY):
                                    self.add_phrase="workout_today"
                                    text=getPhrassesForDelete("workout_today")
                                elif(int(payload[2])==TOMORROW):
                                    self.add_phrase="workout_tomorrow"
                                    text=getPhrassesForDelete("workout_tomorrow")
                                text+="Введите фразу... "

                            post['keyboard']= get_keyboard_notify_change().get_empty_keyboard()
                            self.sender(post)
                else:
                    request=(event.object.message['text']).split()
                    if(request[0]=='start'):
                        _id=event.object.message['from_id']
                        post=self.getPost(_id, "Приветствую!&#129303;\nМогу ли я чем-нибудь помочь? &#128522;")
                        post['keyboard']=get_keyboard_for_admin().get_keyboard()
                        self.sender(post)
                    elif(request[0]=='stop'):
                        _id=event.object.message['from_id']
                        post=self.getPost(_id, "Отключаюсь")
                        post['keyboard']=get_keyboard_for_admin().get_empty_keyboard()
                        self.sender(post)
                        self.stopThread=True
                        break
                    elif((request[0]=='restart')&(len(request)==2)):
                        if(request[1]=='timetable'):
                            self.timetable=restart_timetable()
                            write(self.timetable, 'timetable')
                            post=self.getPost(_id, "Хорошо, я сбросил расписание")
                            self.sender(post)
                        elif(request[1]=='phrasses'):
                            write(restart_phrasses(), "phrasses")
                            post=self.getPost(_id, "Хорошо, я сбросил набор фраз оповещения")
                            self.sender(post)
                    elif(self.delete_phrase.isdigit()==False):
                        print("self.delete_phrase.isdigit()==False")
                        phrasses=read("phrasses")
                        n=len(phrasses[self.delete_phrase])
                        if(request[0].isdigit()):
                            k=int(request[0])
                            if((k>=0)&(k<n)):
                                phrasses[self.delete_phrase].pop(k)
                                write(phrasses, "phrasses")
                                self.delete_phrase="0"
                                text="Удаление фразы прошло успешно. Что-то еще?"
                                post=self.getPost(_id,  text)
                                post['keyboard']=get_keyboard_notify().get_keyboard()
                                self.sender(post)
                            else:#я не сделал разведление на админов
                                text="Нужно вести целое число от 0 до "+str(n-1)+" включительно"
                                post=self.getPost(_id,  text)
                                self.sender(post)
                        else:
                            text="Нужно вести целое число от 0 до "+str(n-1)+" включительно"
                            post=self.getPost(_id,  text)
                            self.sender(post)
                    elif(self.add_phrase.isdigit()==False):
                        print("self.add_phrase.isdigit()==False")
                        phrasses=read("phrasses")
                        tmp=" ".join(request)
                        if((self.add_phrase == 'cancel_tomorrow')|
                        (self.add_phrase == 'cancel_today')|(self.add_phrase == 'no_train')):
                            phrasses[self.add_phrase].append(tmp)
                            write(phrasses,"phrasses")
                            text="Хорошо, мы добавил еще одну фразу на тему "+self.add_phrase+"\nЧто-то еще?"
                        else:
                            time_ind=tmp.find("time")
                            if(time_ind==-1):
                                text="Ой, эту фразу мы не можем добавить, укажите в следующий раз время)"
                            elif((self.add_phrase == 'longrun_tomorrow')|(self.add_phrase == 'longrun_today')):
                                dist_ind=tmp.find("dist")
                                dist_l=tmp.find("{")
                                dist_r=tmp.find("}")
                                dist_correct=((dist_l<dist_ind)&(dist_ind<dist_r))|((dist_l==dist_ind)&(dist_ind==dist_r))
                                temp_ind=tmp.find("temp")
                                temp_l=tmp.find("[")
                                temp_r=tmp.find("]")
                                temp_correct=((temp_l<temp_ind)&(temp_ind<temp_r))|((temp_l==temp_ind)&(temp_ind==temp_r))
                                if((temp>=0)&(dist==-1)):
                                    text="Вы забыли указать дистанцию..."
                                elif(dist_correct & temp_correct):
                                    if((temp_l==-1)|((dist_l<temp_l)&(temp_r<dist_r))):
                                        text="Отлично, мы добавили фразу на тему "+self.add_phrase
                                        phrasses[self.add_phrase].append(tmp)
                                        write(phrasses,"phrasses")
                                    else:
                                        text="Не корректный ввод(\n Попробуйте в следующий раз.\n Что-то еще?"
                                else:
                                    text="Не корректный ввод(\n Попробуйте в следующий раз.\n Что-то еще?"
                            else:
                                text="Отлично, мы добавили фразу на тему "+self.add_phrase
                                phrasses[self.add_phrase].append(tmp)
                                write(phrasses,"phrasses")

                        self.add_phrase="0"
                        post=self.getPost(_id,  text)
                        post['keyboard']=get_keyboard_notify().get_keyboard()
                        self.sender(post)


            elif(event.type == VkBotEventType.MESSAGE_EVENT):
                index = pd.MultiIndex.from_tuples([(event.object.payload[1],event.object.user_id )], names=["survey_id", "user_id"])
                if(index[0] in self.survey.index):
                    last=self.survey.loc[index[0], 'result_last']
                    if(last!=event.object.payload[0]):
                        self.survey.loc[index[0], 'amount_of_change']+=1
                        self.survey.loc[index[0], 'result_last']=event.object.payload[0]
                        self.survey.loc[index[0], 'day']=self.dayOnWeek
                        if(self.survey.loc[index[0], 'result_last'] == SUPER):
                            if(last<4):
                                text='Мы рады, что Вы изменили свое мнение &#128526;'
                            else:
                                text='Странно &#128529;\nНо я рад, что Вы изменили свое мнение &#128568;'
                        elif(self.survey.loc[index[0], 'result_last'] == NORM):
                            if(last==1):
                                text='Жаль, что Вы изменили свое мнение &#128533;'
                            elif(last<4):
                                text='Мы рады, что Вы изменили свое мнение &#128524;'
                            else:
                                text='Странно, но Ваше мнение учтено &#128559;'
                        elif(self.survey.loc[index[0], 'result_last']== BAD):
                            if(last<3):
                                text='Жаль, что Вы изменили свое мнение &#128546;'
                            else:
                                text='Хорошо, Ваше мнение учтено &#128533;'
                        elif(self.survey.loc[index[0], 'result_last']== ABSENT):
                            text='Ой, а мы думали, Вы были &#128517;'
                        self.vk_session.method('messages.sendMessageEventAnswer',
                              {'event_id':event.object.event_id,
                               'user_id': event.object.user_id ,
                                'peer_id': event.object.peer_id ,
                                'event_data':json.dumps({'type':'show_snackbar', 'text':text})
                               })
                    else:
                        text='Мы записали Ваш ответ &#128522;'
                        self.vk_session.method('messages.sendMessageEventAnswer',
                              {'event_id':event.object.event_id,
                               'user_id': event.object.user_id ,
                                'peer_id': event.object.peer_id ,
                                'event_data':json.dumps({'type':'show_snackbar', 'text':text})
                               })
                else:
                    tmp=pd.DataFrame([[event.object.payload[0] ,event.object.payload[0] ,1, self.dayOnWeek]], columns=self.survey.columns, index=index)
                    self.survey=self.survey.append(tmp)
                    if(event.object.payload[0] == SUPER):
                        text='Мы рады, что тренировка понравилась &#128524;\nПриходите еще &#129303;'
                    elif(event.object.payload[0] == NORM):
                        text='Хотелось бы получить обратную связь &#128577;'
                    elif(event.object.payload[0] == BAD):
                        text='Жаль &#128546;'
                    elif(event.object.payload[0] == ABSENT):
                        text='Приходите на тренировку &#128521;'
                    self.vk_session.method('messages.sendMessageEventAnswer',
                              {'event_id':event.object.event_id,
                               'user_id': event.object.user_id ,
                                'peer_id': event.object.peer_id ,
                                'event_data':json.dumps({'type':'show_snackbar', 'text':text})
                          })


    def do_schedule(self):
        while (self.stopThread==False):
            if(self.changeSchedule):
                schedule.clear()
                day=NumConvertToDay[self.dayOnWeek]
                schedule.every().day.at(shiftTime(self.timetable[day]['оповещение'])).do(self.notify)
                #schedule.every().day.at(shiftTime("11:03")).do(self.notify)
                schedule.every().day.at(shiftTime("00:00")).do(self.chageWeekDay)
                schedule.every().day.at(shiftTime("00:01")).do(self.changeSchedule2)


                print('опрос' in self.timetable[day])
                print(self.survey_on)
                if(('опрос' in self.timetable[day])&(self.survey_on==True)):
                    survey_time=self.timetable[day]['опрос']
                    schedule.every().day.at(shiftTime(survey_time[0])).do(self.survey_turn_on)
                    schedule.every().day.at(shiftTime(survey_time[1])).do(self.survey_turn_off)

                self.changeSchedule=False
            schedule.run_pending()
            time.sleep(1)

    def survey_turn_on(self):
        time=datetime.datetime.now()
        survey_id=int(time.year*1e+6+time.month*1e+4+time.day*1e+2+time.hour)
        post=self.getPost(self.chat_id, "Как прошла тренировка? &#128513;", True)
        #post=self.getPost(self.chat_id, "Как прошел полумарафон? &#127939;", True)
        post['keyboard']=get_keyboard_vote(survey_id).get_keyboard()
        self.sender(post)

    def survey_turn_off(self):#)
        self.survey.to_csv(path_or_buf="survey.csv", sep = ',', index_label =['survey_id', 'user_id'] )
        post=self.getPost(self.chat_id, "Опрос окончен &#128522;", True)
        post['keyboard']=get_keyboard_for_admin().get_empty_keyboard()
        self.sender(post)

    def notify(self):
        post=self.getPost(self.chat_id, "@all\n"+self.generate_text(self.dayOnWeek), True)
        self.sender(post)
    def changeSchedule2(self):
        self.changeSchedule=True

    def sender(self, post):
        self.vk_session.method('messages.send',post)
    def getPost(self, _id, text, itIsChat=False):
        if(itIsChat==True):
            return {"chat_id":_id, "message":text, "random_id":0}
        else:
            return {"user_id":_id, "message":text, "random_id":0}

    def chageWeekDay(self):
        if(datetime.datetime.now().hour>20):
            self.dayOnWeek=(datetime.datetime.now().weekday()+1)%7
        else:
            self.dayOnWeek=datetime.datetime.now().weekday()

    #печатает расписание
    def printTimeTable(self):
        text='Расписание тренировок  &#10024;\n'
        for dw in list(self.timetable.keys()):
            s=dw+' '
            if(self.timetable[dw]['тип']==1):#Лонгран
                s+=' Лонгран'
                if('дистанция' in self.timetable[dw]):
                    s+=' на '+str(self.timetable[dw]['дистанция'])+" км "
                    if('темп' in self.timetable[dw]):
                        s+=' с темпом '+str(self.timetable[dw]['темп'])+" мин/км "
                s+=", "+self.timetable[dw]['время']
                s+=', у главного входа ГЗ\n'
                text+=s
            elif(self.timetable[dw]['тип']==2):#Функциональная тренировка
                s+=' Функциональная тренировка, '
                s+=self.timetable[dw]['время']
                s+=', у главного входа ГЗ\n'
                text+=s
            else:#нет тренировки
                pass
        return text


    def getNextWorkout(self):
        now=datetime.datetime.now()
        d=now.weekday()
        day=NumConvertToDay[d]
        time=self.timetable[day]['оповещение']
        hour=int(time[:2])
        minute=int(time[3:])
        if(now.hour>hour|(now.hour==hour& now.minute>minute)):
            d=(d+1)%7
        for i in range(7):
            if(self.timetable[NumConvertToDay[(d+i)%7]]['тип']>0):
                return (d+i)%7
        return -1
    def getNotifyTime(self):
        text='Пн  '+ self.timetable['Пн']['оповещение']+'\n'
        text+='Вт  '+ self.timetable['Вт']['оповещение']+'\n'
        text+='Ср  '+ self.timetable['Ср']['оповещение']+'\n'
        text+='Чт  '+ self.timetable['Чт']['оповещение']+'\n'
        text+='Пт  '+ self.timetable['Пт']['оповещение']+'\n'
        text+='Сб  '+ self.timetable['Сб']['оповещение']+'\n'
        text+='Вс  '+ self.timetable['Вс']['оповещение']+'\n'
        return text
    def generate_text(self, d):
        day=NumConvertToDay[d]
        phrasses=read("phrasses")
        if (self.timetable[day]['тип']==0):
            day=NumConvertToDay[(d+1)%7]
            if(self.timetable[day]['тип']==0):
                return choice(phrasses['no_train'])
            if(self.timetable[day]['отмена']==1):
                return choice(phrasses['cancel_tomorrow'])
            if(self.timetable[day]['тип']==1):
                text=choice(phrasses['longrun_tomorrow'])
                text=text.replace("time", self.timetable[day]['время'])
                if(('дистанция' in self.timetable[day]) & (text.find("dist")!=-1)):
                    text=text.replace("dist", str(self.timetable[day]['дистанция']))
                    text=text.replace("{", "")
                    text=text.replace("}", "")
                    if(("темп" in self.timetable[day])& (text.find("temp")!=-1)):
                        text=text.replace("temp", self.timetable[day]['темп'])
                        text=text.replace("[", "")
                        text=text.replace("]", "")
                    elif(text.find("temp")!=-1):
                        text=text[:text.find("[")]+text[text.find("]")+1:]
                elif(text.find("dist")!=-1):
                    text=text[:text.find("{")]+text[text.find("}")+1:]
                return text
            text=choice(phrasses['workout_tomorrow'])
            return text.replace("time", self.timetable[day]['время'])
        if(self.timetable[day]['отмена']==1):
            self.timetable[day]['отмена']=0
            write(self.timetable,'timetable')
            return choice(phrasses['cancel_today'])
        if(self.timetable[day]['тип']==1):
            text=choice(phrasses['longrun_today'])
            text=text.replace("time", self.timetable[day]['время'])
            if(('дистанция' in self.timetable[day]) & (text.find("dist")!=-1)):
                text=text.replace("dist", str(self.timetable[day]['дистанция']))
                text=text.replace("{", "")
                text=text.replace("}", "")
                if(("темп" in self.timetable[day])& (text.find("temp")!=-1)):
                    text=text.replace("temp", str(self.timetable[day]['темп']))
                    text=text.replace("[", "")
                    text=text.replace("]", "")
                elif(text.find("temp")!=-1):
                    text=text[:text.find("[")]+text[text.find("]")+1:]
            elif(text.find("dist")!=-1):
                text=text[:text.find("{")]+text[text.find("}")+1:]
            return text
        text=choice(phrasses['workout_today'])
        return text.replace("time", self.timetable[day]['время'])
1