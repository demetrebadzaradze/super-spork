from random import choice, randint

def responde(usr_msg:str) -> str:
    if usr_msg == 'hello' or usr_msg == 'hi' or usr_msg == 'hey':
        return choice(['hello','hi','heyy','yooooo','whats up'])
    elif usr_msg == 'gamble':
        return 'your number is ' + str(randint(1,6))
    else:
        return 'exit'