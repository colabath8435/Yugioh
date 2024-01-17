from flask import Flask, render_template, redirect, session, request, url_for, flash
from input_type import input_data
import pymysql

app = Flask(__name__)
# flash 사용 위해 secret_key 임의로 설정
app.config["SECRET_KEY"] = "ABCD"

@app.route("/")
def home():
    return redirect(url_for('mainpage'))


@app.route("/mainpage", methods=["GET", "POST"])
def mainpage():
    if request.method == 'POST':
        if request.form['card_type']=='not_selected':
            flash('카드 종류를 선택해주세요')
            return render_template('mainpage.html')
        elif request.form.get('submission'):
            sql_sender = input_data
            sql_sender.search = request.form.get('searchname')
            sql_sender.card_type = request.form.get('card_type')
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
            print(f'%asdfasdasdaf%')
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

            conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='yu_gi_oh', charset='utf8')
            try:
                curs = conn.cursor()
                curs.execute(query)
                data = curs.fetchall()
            finally:
                conn.close()

            return render_template('search_result.html',template_data=data,template_data_len=len(data))

        elif request.form.get('login'):
            print(request.data)
            return redirect(url_for('login'))

    else:
        return render_template('mainpage.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route("/search_result", methods=["GET", "POST"])
def search_result():
    if request.method == 'POST':
        return redirect(url_for('search_result'))
    else:
        return render_template('search_result.html')

if __name__ == "__main__":
    app.run()