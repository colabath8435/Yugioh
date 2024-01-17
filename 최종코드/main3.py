from flask import Flask, render_template, redirect, session, request, url_for, flash, escape
from flask_sqlalchemy import SQLAlchemy
from input_type import input_data
import worldcup
import pymysql
import time, random

app = Flask(__name__)

@app.route("/")
def home():
    # 처음 접속시 session 초기화(창닫아도 로그아웃 안되는 경우 방지)
    session.clear()
    return redirect(url_for('mainpage'))

@app.route("/mainpage", methods=["GET", "POST"])
def mainpage():
    if request.method == 'POST':
        if request.form.get('submission') and request.form['card_type']=='not_selected':
            flash('카드 종류를 선택해주세요')
            return render_template('mainpage.html')
        elif request.form.get('submission') and 'logFlag' not in session.keys():
            flash('로그인 후 검색 가능합니다')
            return render_template('mainpage.html')
        elif request.form.get('submission'):
            sql_sender = input_data
            sql_sender.search = request.form.get('searchname')
            sql_sender.card_type = request.form.get('card_type')
            session['card_type'] = sql_sender.card_type
            sql_sender.min_level = request.form.get('min_level')
            sql_sender.max_level = request.form.get('max_level')
            sql_sender.ATK_MIN = request.form.get('ATK_MIN')
            sql_sender.ATK_MAX = request.form.get('ATK_MAX')
            sql_sender.DEF_MIN = request.form.get('DEF_MIN')
            sql_sender.DEF_MAX = request.form.get('DEF_MAX')

            sql_sender.atr_list = request.form.getlist('atr')
            sql_sender.icon_list = request.form.getlist('icon')
            sql_sender.type_list = request.form.getlist('type')

            #SELECT * FROM monster_card WHERE monster_type in ('천사족','언데드족') AND attribute in ('빛','땅','화염');
            #f'SELECT * FROM monster_card WHERE {type_filter} AND {attribute_filter}' 
        
            #----------------------------------수정 부분---------------------------------

            # 카드 이름
            if not sql_sender.search:
                name_filter=True
            else:
                name_filter=f'card_name LIKE "%{sql_sender.search}%"'
            # 몬스터 카드 선택
            if request.form['card_type']=='monster':
                
                # 최소 / 최대 레벨
                if not sql_sender.min_level:
                    sql_sender.min_level=0
            
                if not sql_sender.max_level:
                    sql_sender.max_level=12

                level_filter=f'grade_size BETWEEN {sql_sender.min_level} AND {sql_sender.max_level}'

                # 최소 / 최대 공격력
                if not sql_sender.ATK_MIN:
                    sql_sender.ATK_MIN=-1
                if not sql_sender.ATK_MAX:
                    sql_sender.ATK_MAX=5000
                
                atk_filter=f'atk BETWEEN {sql_sender.ATK_MIN} AND {sql_sender.ATK_MAX}'

                # 최소 / 최대 수비력 (미입력시 수비력이 null인 경우도 포함)
                if not (sql_sender.DEF_MIN and sql_sender.DEF_MAX):
                    def_filter='(def IS NULL OR def BETWEEN -1 AND 5000)'
                elif (not sql_sender.DEF_MIN) and sql_sender.DEF_MAX:
                    def_filter=f'(def IS NULL OR def BETWEEN -1 AND {sql_sender.DEF_MAX})'
                else:
                    def_filter=f'def BETWEEN {sql_sender.DEF_MIN} AND {sql_sender.DEF_MAX}'

                # 속성
                if not sql_sender.atr_list:
                    atr_filter=True
                else:
                    atr_list=list(str(sql_sender.atr_list))
                    atr_list[0],atr_list[-1]='(',')'
                    atr_tuple=''.join(atr_list)
                    atr_filter='attribute in '+ atr_tuple

                # 종족
                if not sql_sender.type_list:
                    type_filter=True
                else:
                    type_list=list(str(sql_sender.type_list))
                    type_list[0],type_list[-1]='(',')'
                    type_tuple=''.join(type_list)
                    type_filter='card_type in '+ type_tuple

                # 최종 몬스터 카드 query문
                query=f'''
                        SELECT *
                        FROM monster_card
                        WHERE {name_filter} AND {level_filter} AND {atk_filter} AND {def_filter}
                        AND {atr_filter} AND {type_filter}
                    '''
                # (오른쪽 두 테이블 db서 구현될시 적용) monster_box, belong_monster도 포함한 query문
                # column ㅡ> (monster_card 전체 column, serial_number, card_text) 순
                """
                    query='''
                            SELECT monster_card.* FROM monster_card, belong_monster.serial_number,monster_box.card_text
                            INNER JOIN belong_monster on monster_card.card_name=belong_monster.card_name
                            INNER JOIN belong_monster on belong_monster.card_name=monster_box.card_name
                            WHERE {name_filter} AND {level_filter} AND {atk_filter} AND {def_filter}
                            AND {atr_filter} AND {type_filter}
                        '''
                """

            # 마법 카드 선택
            elif request.form['card_type']=='magic':
                # 효과
                if not sql_sender.icon_list:
                    icon_filter=True
                else:
                    # db의 value에 맞게 수정
                    # ex) ['지속','속공'] ㅡ> ['지속 마법','속공 마법']
                    icon_list=[icon+' 마법' for icon in sql_sender.icon_list]

                    icon_list=list(str(icon_list))
                    icon_list[0],icon_list[-1]='(',')'
                    icon_tuple=''.join(icon_list)
                    icon_filter='icon in '+ icon_tuple

                # 최종 마법 카드 query문
                query=f'''
                        SELECT * 
                        FROM magic_card
                        WHERE {name_filter} AND {icon_filter}
                    '''
            # 함정 카드 선택
            else:
                # 효과
                if not sql_sender.icon_list:
                    icon_filter=True
                else:
                    # db의 value에 맞게 수정
                    # ex) ['일반','카운터'] ㅡ> ['일반 함정','카운터 함정']
                    icon_list=[icon+' 함정' for icon in sql_sender.icon_list]

                    icon_list=list(str(icon_list))
                    icon_list[0],icon_list[-1]='(',')'
                    icon_tuple=''.join(icon_list)
                    icon_filter='icon in '+ icon_tuple
                
                # 최종 함정 카드 query문
                query=f'''
                        SELECT * 
                        FROM trap_card
                        WHERE {name_filter} AND {icon_filter}
                    '''
            # query문 출력값 확인용
            print(query)

            #conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='yu_gi_oh', charset='utf8')
            
            curs = conn.cursor()
            curs.execute(query)
            data = curs.fetchall()
            template_data_len = len(data)
            """finally:
                conn.close()"""
            # 검색 결과들 월드컵 참가 리스트에 넣기
            worldcup.initial_participant_list=list(data)[:]
            return render_template('search_result.html',template_data=data,template_data_len=len(data))
            #return redirect('/search_result', template_data=data , template_data_len=template_data_len)

        # 로그인 버튼
        if request.form.get('login'):
            UserID = request.form.get('id_input')
            Userpw = request.form.get('pw_input')
            curs = conn.cursor(pymysql.cursors.DictCursor)
            #sql = "SELECT ID FROM account where ID =" + '\'' + id + '\''
            sql = "SELECT * FROM account where ID =" + f"'{UserID}'"
            try:
                curs.execute(sql)
                data = curs.fetchall()
                # account table 안에 일치하는 ID 존재 & password와 일치
                if ((data[0]['ID'] == UserID) and (data[0]['password'] == Userpw)):
                    session['logFlag'] = True
                    session['name'] = data[0]['name']
                    session['ID'] = data[0]['ID']
                    session['gender'] = data[0]['gender']
                    session['password'] = data[0]['password']
                    session['birth'] = str(data[0]['birth'])
                    session['email'] = data[0]['email']
                    print('logged in')
                # account table 안에 일치하는 ID 확인 & password와 불일치
                else:
                    flash('비밀번호 아님 아이디 틀림')
                    print('pw or id X')
            # account table 안에 입력된 ID가 없는 경우
            except:
                flash('몰라 그런 이름 없어')
                print('NO SUCH NAME')
            return redirect(url_for('mainpage'))
            
    
        
        elif request.form.get('logout'):
            session.pop('name')
            session.pop('ID')
            session.pop('password')
            session.pop('gender')
            session.pop('birth')
            session.pop('email')
            session.pop('logFlag')
            print('logged out')
            # 1초 시간 지연
            time.sleep(1)
            # session 비었는지 확인
            print(session.keys())
            return redirect(url_for('mainpage'))

        elif request.form.get('register'):
            return redirect(url_for('register'))

        elif request.form.get('change_info'):
            return redirect(url_for('change'))

        return redirect(url_for('mainpage'))
    else:
        return render_template('mainpage.html')

@app.route("/search_result<template_data><template_data_len>", methods=["GET", "POST"])
def search_result(template_data,template_data_len):
    if request.method == 'POST':
        if request.form.get('card_list'):
            data=request.form.get('card_list')
            print('-='*20)
            print(data)
            print(type(data))
            # 여기서 카드 이름만 가져오고 sql문 실행 
            return render_template('card_info.html',data=data)
        return redirect(url_for('search_result'))
    else:
        return render_template('search_result.html', template_data=template_data , template_data_len=template_data_len)

# 카드 검색 결과 페이지에서 개별 카드 정보
@app.route("/card_info", methods=["GET", "POST"])
def card_info():
    ns = request.args.get('row')
    print('-'*20)
    print(ns)
    print(type(ns))
    print('-'*20)
    # 1. 카드 이름 가져오기
    sql_name = request.form.get('card_name')
    print(sql_name)
    # 2. 몬스터 / 마법 / 함정 테이블 중에 어딘지 파악

    # 3. query문 작성해서 해당 카드 이름의 row 가져오기

    return render_template('card_info.html',ns=ns)



# ------------------- 로그인 부분 ---------------------------


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        # 회원가입 버튼
        if request.form.get('register'):
            id = request.form['id']
            password = request.form['password']
            name = request.form['name']
            birth = request.form['birth_date']
            gender = request.form['gender']
            email = request.form['email']
            print('+++++++++++@@@@@@@@@@@@@@@@@@@++++++++++++')
            print(id, password, name, birth, gender, email)
            print('+++++++++++@@@@@@@@@@@@@@@@@@@++++++++++++')
            curs = conn.cursor()
            try:
                sql = "SELECT * FROM account where ID =" + f"'{id}'"
                #sql = "SELECT ID FROM account where ID =" + '\'' + id + '\''
                curs.execute(sql)
                data = curs.fetchone()
                # account 테이블에 동일한 id가 없는 경우
                if type(data) != 'tuple':
                    insert_sql = "INSERT INTO account VALUES (%s, %s, %s, %s, %s, %s)"
                    insert_data = [id, name, password, gender,birth, email]
                    curs.execute(insert_sql, insert_data)
                    conn.commit()
                    flash('성공함')
                    print('성공함')
                else:
                    flash('아이디 중복됨')
                    print('아이디 중복됨')
            except:
                flash('실패함')
                print('실패함')
            return redirect(url_for('mainpage'))
        # 돌아가기 버튼
        else:
            return redirect(url_for('mainpage'))
    else:
        return render_template('register.html')

@app.route("/change", methods=["GET", "POST"])
def change():
    print(155)
    if request.method == 'POST':
        if request.form.get('change'):
            new_pw = request.form.get('password')
            new_gen = request.form.get('gender')
            new_email = request.form.get('email')
            new_bir = request.form.get('birth_date')
            new_name = request.form.get('name')
            ID = session['ID']
            print(new_pw, new_gen, new_email, new_bir, new_name, ID)

            curs = conn.cursor()
    
            sql = "UPDATE account SET name = %s, password = %s, gender = %s, birth = %s, email = %s WHERE ID = %s"
            l = [new_name, new_pw, new_gen, new_bir, new_email,ID]
            curs.execute(sql, l)
            print(12345)
            conn.commit()
            return redirect(url_for('mainpage'))
        else:
            return redirect(url_for('mainpage'))
    else:
        return render_template('change.html')


###################      월드컵 부분        ###################


@app.route("/worldcup_main",methods=['GET','POST'])
def worldcup_main():
    if request.method == 'POST':
        # 선택된 총 라운드 수 만큼의 월드컵 참가 카드를 랜덤하게 고른다
        # (shuffle 한 다음 앞에서부터 라운드 수 만큼의 카드를 선택하는 방식)
        random.shuffle(worldcup.initial_participant_list)
        worldcup.round=int(request.form['select'])
        worldcup.participant_list=worldcup.initial_participant_list[:worldcup.round]
        return redirect(url_for('worldcup_match'))
    return render_template('worldcup_mainpage.html',total_card_num=len(worldcup.initial_participant_list))

@app.route("/worldcup_match")
def worldcup_match():
    # 해당 라운드(O강) 끝났을 때 참가 리스트->승자 리스트, 승자 리스트->빈 리스트로 초기화
    if not worldcup.participant_list:
        worldcup.participant_list=worldcup.winner_list
        worldcup.winner_list=[]
    return render_template('worldcup_match.html',
        left=worldcup.participant_list[0],
        right=worldcup.participant_list[1],
        participant_list=worldcup.participant_list,
        winner_list=worldcup.winner_list,
        len_participant_list=len(worldcup.participant_list),
        len_winner_list=len(worldcup.winner_list),
        cur_round=len(worldcup.participant_list)+2*len(worldcup.winner_list),
        cur_match_order=len(worldcup.winner_list)+1
    )

@app.route("/selected_left")
def selected_left():
    worldcup.winner_list.append(worldcup.participant_list.pop(0))
    worldcup.participant_list.pop(0)
    # 결승전
    if not worldcup.participant_list and len(worldcup.winner_list) == 1:
        return redirect('/winner')
    return redirect(url_for('worldcup_match'))

@app.route("/selected_right")
def selected_right():
    worldcup.participant_list.pop(0)
    worldcup.winner_list.append(worldcup.participant_list.pop(0))
    # 결승전
    if not worldcup.participant_list and len(worldcup.winner_list) == 1:
        return redirect('/winner')
    return redirect(url_for('worldcup_match'))

@app.route("/winner")
def winner():
    winner=worldcup.winner_list.pop(0)
    return render_template('worldcup_winner.html',winner=winner)

@app.route("/go_main")
def go_main():
    return render_template('go_main.html')




'''
@app.route("/search_result", methods=["GET", "POST"])
def search_result():
    if request.method == 'POST':
        return redirect(url_for('search_result'))
    else:
        return render_template('search_result.html')
'''

if __name__ == "__main__":
    app.secret_key = '6hc/_gsh,./;2ZZx3c6_s,1//'
    ################################################
    # db 이름 자기 것으로 수정
    ################################################
    conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='yu_gi_oh', charset='utf8')
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')