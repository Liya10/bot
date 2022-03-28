from vk_api.keyboard import VkKeyboard, VkKeyboardColor

ADMIN=100

SUPER=1
NORM=2
BAD=3
ABSENT=4

CHANGE=10
ADD=11
DELETE=12

SHOW_DAY=15
WORKOUT=16
LONG=17
TOMORROW=18
TODAY=19


CANCEL=20




SURVEY=30
START_THE_COUNT=31
STOP_THE_COUNT=32
SHOW_SURVEY=33

NOTIFY=90




SHOW=50
EXIT=60

MONDAY=71
ALL=70

YES=80
NO=81


def get_keyboard_for_admin():
    keyboard_for_admin=VkKeyboard()
    keyboard_for_admin.add_button('Показажи мне текущее расписание &#128220;', payload=[SHOW])
    keyboard_for_admin.add_line()
    keyboard_for_admin.add_button('Мне нужно изменить расписание &#9997;',  payload=[CHANGE])
    keyboard_for_admin.add_line()
    keyboard_for_admin.add_button('Я хотел бы отменить тренировку &#128567;',  payload=[CANCEL])
    keyboard_for_admin.add_line()
    keyboard_for_admin.add_button('Я по поводу опроса &#9745;&#65039;',  payload=[SURVEY])
    keyboard_for_admin.add_line()
    keyboard_for_admin.add_button('Я по поводу оповещения &#128483;', payload=[NOTIFY])
    keyboard_for_admin.add_line()
    keyboard_for_admin.add_button('Нет, спасибо &#128578;', payload=[EXIT])
    return keyboard_for_admin;

def get_keyboard_survey(on):#опрос начат
    keyboard=VkKeyboard()
    if(on):
        keyboard.add_button('Выключить',  payload=[STOP_THE_COUNT])
    else:
        keyboard.add_button('Включить', VkKeyboardColor.POSITIVE , payload=[START_THE_COUNT])
    keyboard.add_line()
    keyboard.add_button('Да, мне интересны результаты', payload=[SHOW_SURVEY])#покажет текущие голоса
    keyboard.add_line()
    keyboard.add_button('Нет, мимо проходил &#128517;', payload=[ADMIN])
    return keyboard




def get_keyboard_survey_info():#информация опроса
    keyboard=VkKeyboard()
    keyboard.add_button('Пн',  payload=[SURVEY, MONDAY])
    keyboard.add_button('Вт', payload=[SURVEY, MONDAY+1])
    keyboard.add_line()
    keyboard.add_button('Ср',  payload=[SURVEY, MONDAY+2])
    keyboard.add_button('Чт', payload=[SURVEY, MONDAY+3])
    keyboard.add_line()
    keyboard.add_button('Пт',  payload=[SURVEY, MONDAY+4])
    keyboard.add_button('Сб', payload=[SURVEY, MONDAY+5])
    keyboard.add_line()
    keyboard.add_button('Вс',  payload=[SURVEY, MONDAY+6])
    keyboard.add_button('в целом', payload=[SURVEY, ALL])

    return keyboard

NOTIFY_TIME=91
NOTIFY_GET=92
NOTIFY_CHANGE=93

def get_keyboard_notify():
    keyboard=VkKeyboard()
    keyboard.add_button('Я хотел бы изменить время оповещения', payload=[NOTIFY_TIME])
    keyboard.add_line()
    keyboard.add_button('Я хотел бы получить набор фраз',  payload=[NOTIFY_GET])
    keyboard.add_line()
    keyboard.add_button('Я хотел бы изменить фразы', payload=[NOTIFY_CHANGE])
    keyboard.add_line()
    keyboard.add_button('Я передумал', payload=[ADMIN])
    return keyboard

def get_keyboard_notify_time():
    keyboard=VkKeyboard()
    keyboard.add_button('Пн',  payload=[NOTIFY_TIME, MONDAY])
    keyboard.add_button('Вт', payload=[NOTIFY_TIME, MONDAY+1])
    keyboard.add_line()
    keyboard.add_button('Ср',  payload=[NOTIFY_TIME, MONDAY+2])
    keyboard.add_button('Чт', payload=[NOTIFY_TIME, MONDAY+3])
    keyboard.add_line()
    keyboard.add_button('Пт',  payload=[NOTIFY_TIME, MONDAY+4])
    keyboard.add_button('Сб', payload=[NOTIFY_TIME, MONDAY+5])
    keyboard.add_line()
    keyboard.add_button('Вс',  payload=[NOTIFY_TIME, MONDAY+6])
    keyboard.add_button('Меня все устраивает', payload=[NOTIFY])
    return keyboard

def get_keyboard_notify_time_change(day):
    keyboard=VkKeyboard()
    keyboard.add_button('08:00',  payload=[NOTIFY_TIME, day, 8])
    keyboard.add_button('09:00', payload=[NOTIFY_TIME, day, 9])
    keyboard.add_line()
    keyboard.add_button('10:00',  payload=[NOTIFY_TIME, day, 10])
    keyboard.add_button('11:00', payload=[NOTIFY_TIME, day, 11])
    return keyboard

def  get_keyboard_notify_change(tmp=0):
    keyboard=VkKeyboard()
    if(tmp==0):
        keyboard.add_button('Удалить', payload=[NOTIFY_CHANGE, DELETE])
        keyboard.add_line()
        keyboard.add_button('Добавить',  payload=[NOTIFY_CHANGE, ADD])
        return keyboard
    elif(tmp==DELETE):
        keyboard.add_button('Лонгран сегодня', payload=[NOTIFY_CHANGE, DELETE,  LONG, TODAY])
        keyboard.add_button('Лонгран завтра', payload=[NOTIFY_CHANGE, DELETE, LONG, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Функц сегодня', payload=[NOTIFY_CHANGE,DELETE,  WORKOUT, TODAY])
        keyboard.add_button('Функц завтра', payload=[NOTIFY_CHANGE, DELETE, WORKOUT, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Отмена сегодня', payload=[NOTIFY_CHANGE,DELETE,  CANCEL, TODAY])
        keyboard.add_button('Отмена завтра', payload=[NOTIFY_CHANGE, DELETE, CANCEL, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Нет тренировка', payload=[NOTIFY_CHANGE,DELETE, WORKOUT, 0])
        return keyboard
    elif(tmp==ADD):
        keyboard.add_button('Лонгран сегодня', payload=[NOTIFY_CHANGE,ADD, LONG, TODAY])
        keyboard.add_button('Лонгран завтра', payload=[NOTIFY_CHANGE, ADD, LONG, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Функц сегодня', payload=[NOTIFY_CHANGE, ADD, WORKOUT, TODAY])
        keyboard.add_button('Функц завтра', payload=[NOTIFY_CHANGE, ADD, WORKOUT, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Отмена сегодня', payload=[NOTIFY_CHANGE,ADD, CANCEL, TODAY])
        keyboard.add_button('Отмена завтра', payload=[NOTIFY_CHANGE, ADD, CANCEL, TOMORROW])
        keyboard.add_line()
        keyboard.add_button('Нет тренировка', payload=[NOTIFY_CHANGE, ADD, WORKOUT, 0])
        return keyboard


def get_keyboard_cancel():
    keyboard_cancel=VkKeyboard()
    keyboard_cancel.add_button('Ближайшая', payload=[CANCEL, ALL])
    keyboard_cancel.add_button('За понедельник', payload=[CANCEL, MONDAY])
    keyboard_cancel.add_line()
    keyboard_cancel.add_button('За вторник', payload=[CANCEL, MONDAY+1])
    keyboard_cancel.add_button('За среду', payload=[CANCEL, MONDAY+2])
    keyboard_cancel.add_line()
    keyboard_cancel.add_button('За четверг', payload=[CANCEL, MONDAY+3])
    keyboard_cancel.add_button('За пятницу', payload=[CANCEL, MONDAY+4])
    keyboard_cancel.add_line()
    keyboard_cancel.add_button('За субботу', payload=[CANCEL, MONDAY+5])
    keyboard_cancel.add_button('За воскресенье', payload=[CANCEL, MONDAY+6])
    return keyboard_cancel

def get_keyboard_cancel_confirmation(day):
    keyboard_cancel=VkKeyboard()
    keyboard_cancel.add_button('Да', payload=[CANCEL,day, YES])
    keyboard_cancel.add_button('Нет', payload=[ADMIN])
    return keyboard_cancel

def get_keyboard_day():
    keyboard_day=VkKeyboard()
    keyboard_day.add_button('Понедельник', payload=[MONDAY])
    keyboard_day.add_button('Вторник', payload=[MONDAY+1])
    keyboard_day.add_line()
    keyboard_day.add_button('Среда', payload=[MONDAY+2])
    keyboard_day.add_button('Четверг', payload=[MONDAY+3])
    keyboard_day.add_line()
    keyboard_day.add_button('Пятница', payload=[MONDAY+4])
    keyboard_day.add_button('Суббота', payload=[MONDAY+5])
    keyboard_day.add_line()
    keyboard_day.add_button('Воскресенье', payload=[MONDAY+6])
    return  keyboard_day



def get_keyboard_add(day):#в этот день нет тренировки, доступные действия:
    keyboard=VkKeyboard()
    keyboard.add_button('Да, пожалуйста &#128522;', payload=[ADD,day])#get_keyboard_time
    keyboard.add_line()
    keyboard.add_button('Нет, спасибо &#128522;', payload=[ADMIN])
    return keyboard

def get_keyboard_change(day):#есть тренировка, доступные действия изменить или удалить расписание
    keyboard=VkKeyboard()
    keyboard.add_button('удалить тренировку', payload=[DELETE,day])
    keyboard.add_line()
    keyboard.add_button('изменить тренировку', payload=[ADD,day])#get_keyboard_time
    keyboard.add_line()
    keyboard.add_button('ничего не менять', payload=[ADMIN])
    return keyboard

def get_keyboard_delete(day):
    keyboard=VkKeyboard()
    keyboard.add_button('да', payload=[DELETE, YES,day])
    keyboard.add_line()
    keyboard.add_button('нет', payload=[DELETE, NO,day])
    return keyboard

def get_keyboard_type(day,hour,minute):#определить тип тренировки
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('функциональная тренировка', payload=[WORKOUT,day,hour,minute])
    keyboard.add_line()
    keyboard.add_button('Лонгран', payload=[LONG,day,hour,minute])
    return keyboard

NO_DIST=300
DIST_3=NO_DIST+3
DIST_40=NO_DIST+40
def get_keyboard_dist(day,hour,minute,typeWorkout):#нужно ли учитвать дистанцию
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('нет', payload=[NO_DIST,day,hour,minute,typeWorkout])
    keyboard.add_button('3', payload=[NO_DIST+3,day,hour,minute,typeWorkout])
    keyboard.add_button('5', payload=[NO_DIST+5,day,hour,minute,typeWorkout])
    keyboard.add_line()
    keyboard.add_button('7', payload=[NO_DIST+7,day,hour,minute,typeWorkout])
    keyboard.add_button('10', payload=[NO_DIST+10,day,hour,minute,typeWorkout])
    keyboard.add_button('14', payload=[NO_DIST+14,day,hour,minute,typeWorkout])
    keyboard.add_line()
    keyboard.add_button('21', payload=[NO_DIST+21,day,hour,minute,typeWorkout])
    keyboard.add_button('28', payload=[NO_DIST+28,day,hour,minute,typeWorkout])
    keyboard.add_button('40', payload=[NO_DIST+40,day,hour,minute,typeWorkout])
    return keyboard

NO_TEMP=399
TEMP_4=400
TEMP_5=500
TEMP_6=600
TEMP_7=700
def get_keyboard_temp(day,hour,minute,typeWorkout, dist):#нужно ли учитывать темп
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('нет', payload=[NO_TEMP,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('7:00', payload=[TEMP_7,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('6:30', payload=[TEMP_6+30,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('6:00', payload=[TEMP_6,day,hour,minute,typeWorkout, dist])
    keyboard.add_line()
    keyboard.add_button('5:45', payload=[TEMP_5+45,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('5:30', payload=[TEMP_5+30,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('5:15', payload=[TEMP_5+15,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('5:00', payload=[TEMP_5,day,hour,minute,typeWorkout, dist])
    keyboard.add_line()
    keyboard.add_button('4:45', payload=[TEMP_4+45,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('4:30', payload=[TEMP_4+30,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('4:15', payload=[TEMP_4+15,day,hour,minute,typeWorkout, dist])
    keyboard.add_button('4:00', payload=[TEMP_4,day,hour,minute,typeWorkout, dist])
    return keyboard

def get_keyboard_confirmation(day,hour,minute,typeWorkout, dist=0, temp=0):#подтверждения изменении
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('да', payload=[YES,day,hour,minute,typeWorkout, dist, temp])
    keyboard.add_line()
    keyboard.add_button('нет', payload=[NO])
    return keyboard

def get_keyboard_vote(survey_id):
    keyboard_vote=VkKeyboard()
    keyboard_vote.add_callback_button('Супер &#128077;', VkKeyboardColor.POSITIVE, payload=[SUPER,survey_id])
    keyboard_vote.add_line()
    keyboard_vote.add_callback_button('Средне &#128528;', VkKeyboardColor.PRIMARY, payload=[NORM,survey_id])
    keyboard_vote.add_line()
    keyboard_vote.add_callback_button('Отстой &#128078;', VkKeyboardColor.NEGATIVE, payload=[BAD,survey_id])
    keyboard_vote.add_line()
    keyboard_vote.add_callback_button('Не был &#128694;', payload=[ABSENT,survey_id])
    return keyboard_vote

HOUR_8=108
HOUR_9=109
HOUR_10=110
HOUR_11=111
HOUR_12=112
HOUR_13=113
HOUR_14=114
HOUR_15=115
HOUR_16=116
HOUR_17=117
HOUR_18=118
HOUR_19=119

def get_keyboard_hour(day):
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('8', payload=[HOUR_8,day])
    keyboard.add_button('9', payload=[HOUR_9,day])
    keyboard.add_button('10', payload=[HOUR_10,day])
    keyboard.add_line()
    keyboard.add_button('11', payload=[HOUR_11,day])
    keyboard.add_button('12', payload=[HOUR_12,day])
    keyboard.add_button('13', payload=[HOUR_13,day])
    keyboard.add_line()
    keyboard.add_button('14', payload=[HOUR_14,day])
    keyboard.add_button('15', payload=[HOUR_15,day])
    keyboard.add_button('16', payload=[HOUR_16,day])
    keyboard.add_line()
    keyboard.add_button('17', payload=[HOUR_17,day])
    keyboard.add_button('18', payload=[HOUR_18,day])
    keyboard.add_button('19', payload=[HOUR_19,day])
    return keyboard

MIN_0 =120
MIN_5 =125
MIN_10 =130
MIN_15 =135
MIN_20 =140
MIN_25 =145
MIN_30 =150
MIN_35 =155
MIN_40 =160
MIN_45 =165
MIN_50 =170
MIN_55 =175
def get_keyboard_minute(day,hour):
    keyboard=VkKeyboard(one_time=True)
    keyboard.add_button('0', payload=[MIN_0,day,hour])
    keyboard.add_button('5', payload=[MIN_5,day,hour])
    keyboard.add_button('10', payload=[MIN_10,day,hour])
    keyboard.add_line()
    keyboard.add_button('15', payload=[MIN_15,day,hour])
    keyboard.add_button('20', payload=[MIN_20,day,hour])
    keyboard.add_button('25', payload=[MIN_25,day,hour])
    keyboard.add_line()
    keyboard.add_button('30', payload=[MIN_30,day,hour])
    keyboard.add_button('35', payload=[MIN_35,day,hour])
    keyboard.add_button('40', payload=[MIN_40,day,hour])
    keyboard.add_line()
    keyboard.add_button('45', payload=[MIN_45,day,hour])
    keyboard.add_button('50', payload=[MIN_50,day,hour])
    keyboard.add_button('55', payload=[MIN_55,day,hour])
    return keyboard




