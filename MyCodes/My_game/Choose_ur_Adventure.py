#start -> dirty -> right/left ->
def s_dirty():
    print("\nDirty road ahead!")
    while True:
        decision=input("Choose your option\nGo 'right' or 'left': ").lower()
        if decision=="right":
            c_right()
            break
        elif decision=="left":
            c_left()
            break
        else:
            print("\nDanger follows everywhere!\nchoose a valid decisions!!\n")
            continue
def c_right():
    while True:
        decision=input("\nYou found a cute slug.\nWanna kill it?(yes/no) ").lower()
        if decision=="yes":
            print("\nKilled successfully! Exp increased +5\nYou leveled up")
            player_level(5)
            break
        else:
            print("\nLost your chance to gain exp! \nTry next time\n")
            break
def c_left():
    while True:
        decision=input("\nYou found a ugly catapiller.\nWanna kill it?(yes/no) ").lower()
        if decision=="yes":
            print("\nKilled successfully! Exp increased +10\nYou leveled up")
            player_level(10)
            break
        else:
            print("\nLost your chance to gain exp! \nTry next time\n")
            break
#right/left -> resting -> tree/market
def s_resting():
    print("\nYou're tired with all the killing now you wanna rest.\n")
    while True:
        decision=input("You go to under the tree or in the market?(tree/market) ").lower()
        if decision=="tree":
            s_tree()
            break
        elif decision=="market":
            s_market()
            break
        else:
            print("Choose an option please\n")
def s_tree():
    print("While resting you get disturbed by the voices down the streat. \nYou see an agitated crowd marching towards the palace\n")
    while True:
        decision=input("Join them(yes/no): ").lower()
        if decision=="yes":
            s_palace()
            break
        else:
            print("\nYou weren't feeling like resting anymore so you went up and went to jungle.")
            s_cave()
            break
def s_market():
    print("You are in market, a crying aunt approached you seeing your fit body.\nShe told you why she is crying \nApprantly her child was lost in near jungle, she wants you to find them")
    while True:
        decision=input("Wanna help?(yes/no) ").lower()
        if decision=="yes":
            print("You marched your way to jungle and reached it.")
            s_cave()
            break
        else:
            print("Someone noticed your heartless act and approached you. ")
            while True:
                decision=input("He said that if you would like to come to palace?(yes/no) ").lower()
                if decision=="yes":
                    s_palace()
                    break
                else:
                    print("Enter an option please!")
            break


#resting -> tree -> palace(crowd)/cave(kindness)
#resting -> market -> palace(king)/cave(help)
def s_palace():
    print("palace")

def s_cave():
    print("You saw few footprints leading to some place, it was small.\nYou thought it belongs to some child so you followed it and reached at the cave.")
    print("cave")


player_exp=0
def exp_increase(exp):
    global player_exp 
    player_exp+=exp
def player_level(exp=0):
    global player_exp 
    player_exp+=exp
    print("Your Level right now is: ",int(player_exp/5))
    print("Your exp is: ",player_exp)

#Asking if they wanna play or not
def main():
    while True:
        Player=input("\nWanna play?(yes/no) ").lower()
        if Player=='no':
            print("\nGoodBye! :(\n")
            quit()
        else:
            print("\nSurvive the difficulties! :D")
            break
    s_dirty()
    s_resting()

if __name__=="__main__":
    main()