# world cup에 쓰일 전역 변수 ㅡ participate_list(현재 라운드(O강)에 참여하는 카드들의 리스트) 
#                           ㅡ initial_participant_list(검색 결과 나온 카드 전부를 담고 있는 리스트)
#                           ㅡ winner_list(현재 라운드(O강)에서 승리한(선택된) 카드들의 리스트)
# 월드컵 한 번 끝나면 변수는 participate_list는 shuffle된 전체 카드 리스트로, winner_list는 []로 초기화됨 


initial_participant_list=[]
participant_list=[]
winner_list=[]
loser_list=[]
round=0

name_filter=''